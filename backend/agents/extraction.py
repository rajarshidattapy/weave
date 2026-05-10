"""
Extraction Agent — extracts the full normalized component schema from a page.

Input:  component URL + library name
Output: normalized component dict matching the unified schema from fix.md
"""
import logging
import json
import os
import hashlib
import re

from openai import OpenAI
from tools.scraper import scrape_url

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

# Library-specific architecture hints injected into the extraction prompt
LIBRARY_HINTS = {
    "shadcn": (
        "shadcn/ui uses MDX + registry. Components are copy-paste via "
        "'npx shadcn@latest add <name>'. They wrap Radix UI primitives with Tailwind CSS. "
        "Look for 'Usage', 'Installation', 'Props' sections and multiple TSX examples."
    ),
    "radix": (
        "Radix UI has Primitives (unstyled, accessible) and Themes (styled layer). "
        "Primitives export sub-components like Accordion.Root, Accordion.Item. "
        "Look for anatomy sections, API reference tables with detailed prop types."
    ),
    "magic": (
        "Magic UI adds animated wrapper components over shadcn/radix. "
        "Uses framer-motion. Install via 'npx magicui-cli@latest add <name>'. "
        "Look for animation props and preview demos."
    ),
    "watermelon": (
        "Watermelon UI is a registry marketplace with premium copy-paste components. "
        "Similar to shadcn structure. Look for 'Dependencies', 'Installation', code tabs."
    ),
}


def extract_component(url: str, library_name: str = "") -> dict | None:
    """
    Scrape a component page and extract the full normalized schema.

    Returns the unified schema dict or None on failure.
    """
    logger.info(f"Extracting component from {url}")

    page = scrape_url(url, use_browser=True)
    if not page or not page.get("markdown"):
        logger.warning(f"Failed to scrape {url}")
        return None

    markdown = page["markdown"]
    # Reject pages that returned essentially nothing (404, auth walls, etc.)
    if len(markdown.strip()) < 300 or "This page could not be found" in markdown:
        logger.warning(f"Page content too thin for {url} ({len(markdown)} chars) — skipping")
        return None

    extracted = _extract_with_llm(url, markdown, library_name)
    if not extracted:
        return None

    component_name = extracted.get("component_name") or extracted.get("name", "")
    # Derive name from URL slug when LLM returns nothing useful
    if not component_name or component_name.lower() in ("unknown", ""):
        slug_from_url = url.rstrip("/").split("/")[-1]
        component_name = slug_from_url.replace("-", " ").title()
        extracted["component_name"] = component_name
        extracted.setdefault("slug", slug_from_url)

    component_id = hashlib.sha256(
        f"{library_name}:{component_name}:{url}".encode()
    ).hexdigest()[:16]

    normalized = _normalize(extracted, component_id, url, library_name, markdown)
    _save_raw(component_id, markdown)
    return normalized


def _extract_with_llm(url: str, markdown: str, library_name: str) -> dict | None:
    """Use OpenAI to extract the full component schema from page markdown."""
    truncated = markdown[:12000]

    lib_hint = ""
    for key, hint in LIBRARY_HINTS.items():
        if key.lower() in library_name.lower():
            lib_hint = f"\nLibrary architecture: {hint}"
            break

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a UI component library parser. Extract ALL information from "
                        "the documentation page markdown into a comprehensive JSON object.\n\n"
                        "Return a JSON object with these exact fields:\n"
                        "- component_name: string (e.g. 'Accordion')\n"
                        "- slug: string (e.g. 'accordion')\n"
                        "- category: string (navigation|overlay|data-entry|layout|feedback|display|form|media)\n"
                        "- description: string (1-3 sentences)\n"
                        "- installation: {\n"
                        "    cli: [] — CLI commands like 'npx shadcn@latest add accordion'\n"
                        "    npm: [] — package manager install commands\n"
                        "    registry: [] — registry/CDN URLs\n"
                        "  }\n"
                        "- dependencies: [] — npm package names (e.g. '@radix-ui/react-accordion')\n"
                        "- imports: [] — import statements from code examples\n"
                        "- props: [{name, type, default, required, description}] — from Props/API tables\n"
                        "- variants: [{name, description}] — named variants or visual states\n"
                        "- examples: [{label, description, code, language}] — each named example\n"
                        "- code_blocks: [{type, language, content, label}] — EVERY code block found.\n"
                        "  type must be one of: component|demo|install|config|import|utility\n"
                        "- accessibility: [] — accessibility notes, ARIA roles, keyboard nav info\n"
                        "- styling: {\n"
                        "    tailwind: bool — uses Tailwind utility classes\n"
                        "    css_in_js: bool — uses CSS-in-JS (styled-components, emotion)\n"
                        "    radix: bool — wraps or uses Radix UI primitives\n"
                        "    motion: bool — uses framer-motion or CSS animations\n"
                        "  }\n"
                        "- composition: {\n"
                        "    primitive: bool — base unstyled component\n"
                        "    composite: bool — composed of multiple sub-components\n"
                        "    wrapper: bool — thin wrapper over another library\n"
                        "  }\n"
                        "- related_components: [] — names of related components mentioned\n"
                        "- framework_compatibility: [] — e.g. ['React', 'Next.js']\n"
                        "- animation_libs: [] — e.g. ['framer-motion', 'tailwind-animate']\n\n"
                        "Be thorough: extract every code block, every prop row, every variant. "
                        "Use null for missing strings, [] for missing arrays, false for missing booleans."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Library: {library_name}{lib_hint}\n"
                        f"URL: {url}\n\n"
                        f"Page content:\n{truncated}"
                    ),
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        logger.error(f"LLM extraction failed for {url}: {e}")
        return None


def _normalize(
    extracted: dict,
    component_id: str,
    url: str,
    library_name: str,
    markdown: str,
) -> dict:
    """Normalize LLM output into the canonical unified schema."""
    name = extracted.get("component_name") or extracted.get("name") or "Unknown"
    slug = extracted.get("slug") or re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    # Ensure installation dict has all three keys
    installation = extracted.get("installation") or {}
    if not isinstance(installation, dict):
        installation = {}
    installation.setdefault("cli", [])
    installation.setdefault("npm", [])
    installation.setdefault("registry", [])

    # Backwards-compat install_command (first CLI command found)
    install_command = (
        installation["cli"][0]
        if installation["cli"]
        else installation["npm"][0]
        if installation["npm"]
        else None
    )

    styling = extracted.get("styling") or {}
    if not isinstance(styling, dict):
        styling = {}
    styling.setdefault("tailwind", False)
    styling.setdefault("css_in_js", False)
    styling.setdefault("radix", False)
    styling.setdefault("motion", False)

    composition = extracted.get("composition") or {}
    if not isinstance(composition, dict):
        composition = {}
    composition.setdefault("primitive", False)
    composition.setdefault("composite", False)
    composition.setdefault("wrapper", False)

    code_blocks = extracted.get("code_blocks") or []

    # Derive tsx_code: prefer first block classified as "component"
    tsx_code = None
    for block in code_blocks:
        if isinstance(block, dict) and block.get("type") == "component":
            tsx_code = block.get("content")
            break
    if not tsx_code:
        for ex in (extracted.get("examples") or []):
            if isinstance(ex, dict) and ex.get("code"):
                lang = (ex.get("language") or "").lower()
                if lang in ("tsx", "jsx", "typescript", "javascript", ""):
                    tsx_code = ex["code"]
                    break

    category = extracted.get("category") or extracted.get("component_type")

    return {
        # Core identity
        "id": component_id,
        "name": name,
        "slug": slug,
        "category": category,
        "source_library": library_name,
        "source_url": url,
        "component_type": category,
        "description": extracted.get("description"),
        # Installation
        "installation": installation,
        "install_command": install_command,
        # Code
        "dependencies": extracted.get("dependencies") or [],
        "imports": extracted.get("imports") or [],
        "tsx_code": tsx_code,
        "code_blocks": code_blocks,
        # API
        "props": extracted.get("props") or [],
        "variants": extracted.get("variants") or [],
        "examples": extracted.get("examples") or [],
        # Docs
        "accessibility": extracted.get("accessibility") or [],
        "preview_images": extracted.get("preview_images") or [],
        "related_components": extracted.get("related_components") or [],
        "framework_compatibility": extracted.get("framework_compatibility") or [],
        "animation_libs": extracted.get("animation_libs") or [],
        # Classification
        "styling": styling,
        "composition": composition,
        # Raw storage
        "raw_docs": markdown[:5000],
    }


def _save_raw(component_id: str, markdown: str):
    """Save raw markdown to storage/raw/."""
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    with open(os.path.join(raw_dir, f"{component_id}.md"), "w", encoding="utf-8") as f:
        f.write(markdown)
