"""
Graph Agent — generates component relationship graphs from stored components.

Produces:
  - dependency_graph:  component -> npm packages it depends on
  - composition_graph: component -> related/sub-components
  - wrapper_graph:     component -> what library it wraps
  - library_lineage:   static layering map (Radix → shadcn → Magic UI)
"""
import json
import os
import logging
from datetime import datetime

from database.models import get_all_components, get_components_by_library

logger = logging.getLogger(__name__)

# Known library lineage (static knowledge from fix.md)
LIBRARY_LINEAGE = {
    "radix": "base-primitive",
    "shadcn": "wraps radix-primitives",
    "magic-ui": "wraps shadcn + radix",
    "magicui": "wraps shadcn + radix",
    "watermelon": "registry-marketplace over shadcn patterns",
}


def generate_graph(library_name: str = None) -> dict:
    """
    Build relationship graphs from all stored components (or one library).

    Returns a dict suitable for /graph endpoint and graph.json storage.
    """
    if library_name:
        components = get_components_by_library(library_name)
    else:
        components = get_all_components(limit=1000)

    dependency_graph: dict[str, list[str]] = {}
    composition_graph: dict[str, list[str]] = {}
    wrapper_graph: dict[str, dict] = {}

    for comp in components:
        name = comp.get("name", "unknown")
        lib = (comp.get("source_library") or "").lower()

        # Dependency graph: component → npm packages
        deps = comp.get("dependencies") or []
        if isinstance(deps, str):
            try:
                deps = json.loads(deps)
            except Exception:
                deps = []
        dependency_graph[name] = deps

        # Composition/related graph
        related = comp.get("related_components") or []
        if isinstance(related, str):
            try:
                related = json.loads(related)
            except Exception:
                related = []
        composition_graph[name] = related

        # Wrapper graph: detect what this component wraps
        styling = comp.get("styling") or {}
        composition = comp.get("composition") or {}
        if isinstance(styling, str):
            try:
                styling = json.loads(styling)
            except Exception:
                styling = {}
        if isinstance(composition, str):
            try:
                composition = json.loads(composition)
            except Exception:
                composition = {}

        wrapped = _detect_wrapped_lib(deps, styling, composition, lib)
        if wrapped:
            wrapper_graph[name] = {
                "wraps": wrapped,
                "library": lib,
                "source_url": comp.get("source_url"),
            }

    # Build library-level lineage from actual stored data
    stored_libs = {(c.get("source_library") or "").lower() for c in components}
    lineage = {lib: LIBRARY_LINEAGE[lib] for lib in stored_libs if lib in LIBRARY_LINEAGE}

    result = {
        "generated_at": datetime.utcnow().isoformat(),
        "component_count": len(components),
        "dependency_graph": dependency_graph,
        "composition_graph": composition_graph,
        "wrapper_graph": wrapper_graph,
        "library_lineage": lineage,
    }

    _save_graph(result, library_name)
    return result


def _detect_wrapped_lib(
    deps: list[str],
    styling: dict,
    composition: dict,
    lib_name: str,
) -> str | None:
    """Infer what library a component wraps based on its deps and classification."""
    dep_str = " ".join(deps).lower()

    if "@radix-ui" in dep_str or styling.get("radix"):
        if "shadcn" in lib_name or "magic" in lib_name or "watermelon" in lib_name:
            return "radix-ui"
    if "framer-motion" in dep_str or styling.get("motion"):
        if "magic" in lib_name:
            return "shadcn + framer-motion"
    if composition.get("wrapper"):
        return "unknown"
    return None


def _save_graph(graph: dict, library_name: str = None):
    """Persist graph.json to storage/."""
    storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
    os.makedirs(storage_dir, exist_ok=True)
    filename = f"graph_{library_name}.json" if library_name else "graph.json"
    filepath = os.path.join(storage_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    logger.info(f"Graph saved to {filepath}")
