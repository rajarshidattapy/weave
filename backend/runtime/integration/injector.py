"""
Injector — orchestrates the full agentic integration pipeline.

Flow:
  1. Generate integration plan (LLM)
  2. Install dependencies
  3. Create component + utility files
  4. Apply target-file modifications via AST manager (LLM-based edits)
  5. Validate build (tsc --noEmit)
  6. Auto-fix errors and retry (up to max_fix_attempts)
"""
import logging
import os
from typing import Callable

from .planner import generate_plan
from .dependency_manager import install
from .ast_manager import add_import, inject_jsx, modify_file
from .validator import validate
from .fixer import fix_errors

logger = logging.getLogger(__name__)

SANDBOX_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "test-next")
)


def run_pipeline(
    component: dict,
    target_file: str = "app/page.tsx",
    on_progress: Callable[[str, str], None] | None = None,
    max_fix_attempts: int = 3,
    sandbox_root: str | None = None,
) -> dict:
    """
    Run the full agentic integration pipeline for a component.

    on_progress(step, message) is called at each stage for real-time streaming.
    """
    root = sandbox_root or SANDBOX_ROOT

    result: dict = {
        "success": False,
        "plan": None,
        "files_created": [],
        "imports_added": [],
        "jsx_injected": [],
        "dependencies_installed": [],
        "build_errors": [],
        "fixes_applied": 0,
        "error": None,
    }

    def emit(step: str, msg: str):
        logger.info(f"[{step}] {msg}")
        if on_progress:
            try:
                on_progress(step, msg)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # 1. Generate integration plan
    # ------------------------------------------------------------------
    name = component.get("name", "Component")
    emit("planning", f"Planning integration for {name}…")

    existing: dict[str, str] = {}
    target_abs = os.path.join(root, target_file)
    if os.path.isfile(target_abs):
        with open(target_abs, encoding="utf-8") as f:
            existing[target_file] = f.read()

    plan = generate_plan(component, target_file, existing)

    if "error" in plan:
        result["error"] = plan["error"]
        emit("error", result["error"])
        return result

    result["plan"] = plan

    # ------------------------------------------------------------------
    # 2. Install dependencies
    # ------------------------------------------------------------------
    all_deps = list({
        *(plan.get("dependencies") or []),
        *(component.get("dependencies") or []),
    })
    if all_deps:
        emit("dependencies", f"Installing {len(all_deps)} package(s)…")
        dep_res = install(all_deps, root)
        result["dependencies_installed"] = dep_res.get("installed", [])
        if dep_res.get("installed"):
            emit("dependencies", f"Installed: {', '.join(dep_res['installed'])}")

    # ------------------------------------------------------------------
    # 3. Create component file
    # ------------------------------------------------------------------
    comp_file = plan.get("component_file")
    if comp_file and comp_file.get("path") and comp_file.get("content"):
        rel = comp_file["path"]
        abs_path = os.path.join(root, rel)
        emit("creating", f"Creating {rel}…")
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(comp_file["content"])
        result["files_created"].append(rel)

    # ------------------------------------------------------------------
    # 4. Create utility / hook / lib files
    # ------------------------------------------------------------------
    for util in plan.get("utility_files") or []:
        rel = util.get("path", "")
        content = util.get("content", "")
        if not rel or not content:
            continue
        abs_path = os.path.join(root, rel)
        if os.path.isfile(abs_path):
            emit("creating", f"Utility {rel} already exists — skipping")
            continue
        emit("creating", f"Creating utility {rel}…")
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        result["files_created"].append(rel)

    # ------------------------------------------------------------------
    # 5. Apply target-file modifications
    # ------------------------------------------------------------------
    for mod in plan.get("target_modifications") or []:
        rel = mod.get("path", target_file)
        abs_path = os.path.join(root, rel)
        action = mod.get("action", "")

        if action == "add_import":
            stmt = mod.get("import_statement", "")
            if stmt:
                emit("importing", f"Adding import to {rel}…")
                add_import(abs_path, stmt)
                result["imports_added"].append(stmt)

        elif action == "inject_jsx":
            snippet = mod.get("jsx_snippet", "")
            location = mod.get("location", "as last child of <main>")
            if snippet:
                emit("injecting", f"Injecting {snippet} into {rel}…")
                inject_jsx(abs_path, snippet, location)
                result["jsx_injected"].append(snippet)

        elif action == "modify":
            instruction = mod.get("instruction", "")
            if instruction:
                emit("modifying", f"Modifying {rel}…")
                modify_file(abs_path, instruction)

    # ------------------------------------------------------------------
    # 6. Validate build
    # ------------------------------------------------------------------
    emit("validating", "Running TypeScript type check…")
    validation = validate(root)

    if validation["success"]:
        result["success"] = True
        emit("complete", f"✓ {name} integrated successfully")
        return result

    result["build_errors"] = validation["errors"]
    emit("fixing", f"Found {len(validation['errors'])} type error(s) — starting auto-fix…")

    # ------------------------------------------------------------------
    # 7. Auto-fix loop
    # ------------------------------------------------------------------
    context_files = result["files_created"] + [target_file]

    for attempt in range(1, max_fix_attempts + 1):
        emit("fixing", f"Fix attempt {attempt}/{max_fix_attempts}…")

        fix_res = fix_errors(
            validation["errors"],
            validation["raw_output"],
            root,
            context_files,
        )

        if not fix_res.get("patches"):
            emit("fixing", "No patchable errors found — stopping")
            break

        result["fixes_applied"] += 1
        validation = validate(root)

        if validation["success"]:
            result["success"] = True
            result["build_errors"] = []
            emit("complete", f"✓ {name} integrated (fixed in {attempt} pass(es))")
            return result

        result["build_errors"] = validation["errors"]

    result["error"] = (
        f"Build still failing after {result['fixes_applied']} fix attempt(s). "
        f"Remaining errors: {len(result['build_errors'])}"
    )
    emit("error", result["error"])
    return result
