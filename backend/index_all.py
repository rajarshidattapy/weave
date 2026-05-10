#!/usr/bin/env python3
"""
Weave Bulk Indexer -- discovers and indexes all components from all 4 target libraries.

Usage:
  cd backend
  python index_all.py                    # all libraries
  python index_all.py --library shadcn   # one library only
  python index_all.py --limit 20         # cap per library
"""
import argparse
import hashlib
import logging
import os
import sys
import time

# Force UTF-8 output on Windows so progress text doesn't crash
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from database.models import (
    init_db, insert_component, get_all_components,
    component_exists_by_url,
)
from agents.discovery import discover_components
from agents.extraction import extract_component
from agents.metadata import generate_metadata

# ---------------------------------------------------------------------------
# Known component slugs per library — used as seeds when discovery is slow
# or returns sparse results. Covers the 12 priority items from fix.md plus
# the most common UI building blocks.
# ---------------------------------------------------------------------------

SHADCN_SLUGS = [
    "accordion", "alert", "alert-dialog", "avatar", "badge", "button",
    "calendar", "card", "carousel", "checkbox", "collapsible", "command",
    "combobox", "context-menu", "data-table", "date-picker", "dialog",
    "drawer", "dropdown-menu", "form", "hover-card", "input", "input-otp",
    "label", "menubar", "navigation-menu", "pagination", "popover",
    "progress", "radio-group", "resizable", "scroll-area", "select",
    "separator", "sheet", "sidebar", "skeleton", "slider", "sonner",
    "switch", "table", "tabs", "textarea", "toast", "toggle", "tooltip",
]

RADIX_SLUGS = [
    "accordion", "alert-dialog", "aspect-ratio", "avatar", "checkbox",
    "collapsible", "context-menu", "dialog", "dropdown-menu", "form",
    "hover-card", "label", "menubar", "navigation-menu", "popover",
    "progress", "radio-group", "scroll-area", "select", "separator",
    "slider", "switch", "tabs", "toast", "toggle", "toggle-group",
    "toolbar", "tooltip",
]

MAGICUI_SLUGS = [
    "animated-beam", "animated-gradient-text", "animated-list",
    "animated-subscribe-button", "aurora-text", "border-beam",
    "bento-grid", "blur-fade", "box-reveal", "confetti", "dock",
    "dot-pattern", "file-tree", "flip-text", "globe", "gradual-spacing",
    "grid-pattern", "hyper-text", "magic-card", "marquee",
    "meteor-shower", "morphing-text", "neon-gradient-card",
    "number-ticker", "orbit", "particles", "pulsating-button",
    "rainbow-button", "retro-grid", "ripple", "safari",
    "scroll-based-velocity", "shimmer-button", "shine-border",
    "shiny-button", "sparkles-text", "text-animate", "text-reveal",
    "word-fade-in", "word-pullup", "word-rotate",
]

WATERMELON_SLUGS = [
    "accordion", "badge", "button", "card", "checkbox", "command",
    "dialog", "dropdown-menu", "input", "navigation-menu", "popover",
    "progress", "radio-group", "select", "separator", "sheet",
    "skeleton", "slider", "switch", "table", "tabs", "textarea",
    "toast", "toggle", "tooltip",
]

LIBRARIES = [
    {
        "name": "shadcn/ui",
        "base_url": "https://ui.shadcn.com/docs/components",
        "component_url_pattern": "https://ui.shadcn.com/docs/components/{slug}",
        "slugs": SHADCN_SLUGS,
    },
    {
        "name": "Radix UI",
        "base_url": "https://www.radix-ui.com/primitives/docs/components",
        "component_url_pattern": "https://www.radix-ui.com/primitives/docs/components/{slug}",
        "slugs": RADIX_SLUGS,
    },
    {
        "name": "Magic UI",
        "base_url": "https://magicui.design/docs/components",
        "component_url_pattern": "https://magicui.design/docs/components/{slug}",
        "slugs": MAGICUI_SLUGS,
    },
    {
        "name": "Watermelon UI",
        "base_url": "https://ui.watermelon.sh/components",
        "component_url_pattern": "https://ui.watermelon.sh/components/{slug}",
        "slugs": WATERMELON_SLUGS,
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _comp_id(library: str, slug: str, url: str) -> str:
    return hashlib.sha256(f"{library}:{slug}:{url}".encode()).hexdigest()[:16]


def _already_indexed(url: str, library: str = "") -> bool:
    """Check by source_url — reliable regardless of how the component name was extracted."""
    return component_exists_by_url(url)


def _seed_urls(lib: dict) -> list[str]:
    """Build the full URL list from known slugs."""
    return [
        lib["component_url_pattern"].format(slug=s)
        for s in lib["slugs"]
    ]


def _discover_extra_urls(lib: dict) -> list[str]:
    """
    Try discovery agent to find URLs beyond the seed list.
    Returns empty list on any failure -- seeds are always the reliable fallback.
    """
    try:
        discovered = discover_components(lib["name"], lib["base_url"])
        # Only return URLs that look like individual component pages
        filtered = [
            u for u in discovered
            if any(seg in u for seg in ["/components/", "/docs/components/"])
            and u.rstrip("/").split("/")[-1] not in ("", "components", "docs")
        ]
        return filtered
    except Exception as e:
        logger.warning(f"Discovery skipped for {lib['name']}: {e}")
        return []


def _index_url(url: str, library_name: str) -> tuple[bool, str]:
    """
    Extract + tag + store one component.
    Returns (success, component_name).
    """
    if _already_indexed(url, library_name):
        slug = url.rstrip("/").split("/")[-1]
        return True, f"[skip] {slug}"

    component = extract_component(url, library_name)
    if not component:
        return False, url

    meta = generate_metadata(
        component.get("name", ""),
        component.get("tsx_code", ""),
        component.get("description", ""),
    )
    component.update({
        "tags": meta.get("tags", []),
        "styles": meta.get("styles", []),
        "embedding_text": meta.get("embedding_text", ""),
    })

    insert_component(component)
    return True, component.get("name", url.split("/")[-1])


# ---------------------------------------------------------------------------
# Per-library indexer
# ---------------------------------------------------------------------------

def index_library(lib: dict, limit: int | None = None, skip_discover: bool = False) -> dict:
    name = lib["name"]
    print(f"\n{'='*56}")
    print(f"  {name}")
    print(f"{'='*56}")

    # Build URL list: seeds + discovered (deduped)
    seed_urls = _seed_urls(lib)
    print(f"  Seed URLs   : {len(seed_urls)}")

    if skip_discover:
        extra_urls: list[str] = []
        print(f"  Discovery   : skipped (--no-discover)")
    else:
        extra_urls = _discover_extra_urls(lib)
        print(f"  Discovered  : {len(extra_urls)} extra")

    all_urls = list(dict.fromkeys(seed_urls + extra_urls))  # preserve order, dedup
    print(f"  Total unique: {len(all_urls)}")

    if limit:
        all_urls = all_urls[:limit]
        print(f"  Capped at   : {limit}")

    already = sum(1 for u in all_urls if _already_indexed(u, name))
    todo = len(all_urls) - already
    print(f"  Already done: {already}  |  To scrape: {todo}\n")

    indexed = skipped = errors = 0
    t0 = time.time()

    for i, url in enumerate(all_urls, 1):
        slug = url.rstrip("/").split("/")[-1]
        try:
            ok, comp_name = _index_url(url, name)
            if "[skip]" in comp_name:
                skipped += 1
                print(f"  [{i:>3}/{len(all_urls)}] -- {slug}")
            elif ok:
                indexed += 1
                elapsed = time.time() - t0
                rate = indexed / elapsed if elapsed else 0
                print(f"  [{i:>3}/{len(all_urls)}] OK {comp_name:<35} ({rate:.1f}/s)")
            else:
                errors += 1
                print(f"  [{i:>3}/{len(all_urls)}] !! {slug}  (extraction failed)")
        except Exception as exc:
            errors += 1
            print(f"  [{i:>3}/{len(all_urls)}] !! {slug}  ({exc})")

    return {
        "library": name,
        "total_urls": len(all_urls),
        "indexed": indexed,
        "skipped": skipped,
        "errors": errors,
        "elapsed_s": round(time.time() - t0, 1),
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Weave bulk component indexer")
    parser.add_argument("--library", help="Index only this library (shadcn|radix|magic|watermelon)")
    parser.add_argument("--limit", type=int, default=None, help="Max components per library")
    parser.add_argument("--no-discover", action="store_true", help="Skip discovery, use seed URLs only")
    args = parser.parse_args()

    print("\n" + "="*56)
    print("         WEAVE  -  Bulk Component Indexer")
    print("="*56)

    if not os.environ.get("ANAKIN_API_KEY"):
        print("\nERROR: ANAKIN_API_KEY not set in .env -- scraping disabled.")
        sys.exit(1)
    if not os.environ.get("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY not set in .env -- LLM extraction disabled.")
        sys.exit(1)

    init_db()

    pre_count = len(get_all_components(limit=10000))
    print(f"\n  DB currently holds {pre_count} components\n")

    targets = LIBRARIES
    if args.library:
        key = args.library.lower()
        targets = [
            lib for lib in LIBRARIES
            if key in lib["name"].lower()
        ]
        if not targets:
            print(f"Unknown library '{args.library}'. Options: shadcn, radix, magic, watermelon")
            sys.exit(1)

    results = []
    grand_start = time.time()

    for lib in targets:
        try:
            r = index_library(lib, limit=args.limit, skip_discover=args.no_discover)
            results.append(r)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user - saving partial results.")
            break
        except Exception as e:
            print(f"\nERROR: Fatal error indexing {lib['name']}: {e}")
            results.append({
                "library": lib["name"], "total_urls": 0,
                "indexed": 0, "skipped": 0, "errors": 1, "elapsed_s": 0,
            })

    # -----------------------------------------------------------------------
    # Summary table
    # -----------------------------------------------------------------------
    post_count = len(get_all_components(limit=10000))
    total_elapsed = round(time.time() - grand_start, 1)

    print(f"\n{'='*56}")
    print("  SUMMARY")
    print(f"{'='*56}")
    print(f"  {'Library':<22} {'URLs':>5} {'New':>5} {'Skip':>5} {'Err':>5}  {'Time':>6}")
    print(f"  {'-'*22} {'-'*5} {'-'*5} {'-'*5} {'-'*5}  {'-'*6}")
    total_new = 0
    for r in results:
        total_new += r["indexed"]
        print(
            f"  {r['library']:<22} {r['total_urls']:>5} {r['indexed']:>5} "
            f"{r['skipped']:>5} {r['errors']:>5}  {r['elapsed_s']:>5.0f}s"
        )
    print(f"  {'-'*56}")
    print(f"  {'TOTAL':<22} {'':>5} {total_new:>5} {'':>5} {'':>5}  {total_elapsed:>5.0f}s")
    print(f"\n  DB before: {pre_count}  ->  after: {post_count}  (+{post_count - pre_count})")
    print()


if __name__ == "__main__":
    main()
