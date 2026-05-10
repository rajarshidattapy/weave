"""
Test script — verifies the scraping pipeline produces the full normalized schema.

Tests one component from each of the 4 target libraries:
  - shadcn/ui        https://ui.shadcn.com/docs/components/accordion
  - Radix UI Themes  https://www.radix-ui.com/themes/docs/components/accordion
  - Magic UI         https://magicui.design/docs/components/accordion
  - Watermelon UI    https://ui.watermelon.sh/components  (landing used as probe)

Run:
  cd backend && python test_scraping.py
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Make sure imports resolve from backend/
sys.path.insert(0, os.path.dirname(__file__))

from agents.extraction import extract_component

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------
TARGETS = [
    {
        "library": "shadcn/ui",
        "url": "https://ui.shadcn.com/docs/components/accordion",
        "expected_fields": ["props", "code_blocks", "installation", "styling"],
    },
    {
        # Radix Themes has no Accordion — it lives in Radix Primitives
        "library": "Radix UI",
        "url": "https://www.radix-ui.com/primitives/docs/components/accordion",
        "expected_fields": ["props", "code_blocks", "accessibility", "composition"],
    },
    {
        # Magic UI shimmer-button is a well-known, reliably-scraped component
        "library": "Magic UI",
        "url": "https://magicui.design/docs/components/shimmer-button",
        "expected_fields": ["code_blocks", "animation_libs", "styling"],
    },
    {
        # Watermelon shows demo previews only; code is in an interactive tab
        # that requires Playwright click() — scraper captures name/description/structure
        "library": "Watermelon UI",
        "url": "https://ui.watermelon.sh/components/accordion",
        "expected_fields": ["name", "description", "slug"],  # code_blocks needs tab interaction
    },
]

# Fields that must be non-empty for a successful extraction
REQUIRED_FIELDS = ["name", "description", "source_url", "source_library"]
RICH_FIELDS = [
    "slug", "category", "installation", "dependencies", "props",
    "variants", "code_blocks", "accessibility", "styling", "composition",
    "related_components",
]


def check_field(component: dict, field: str) -> tuple[bool, str]:
    """Return (ok, summary) for a field."""
    val = component.get(field)
    if val is None:
        return False, "null"
    if isinstance(val, (list, dict)) and not val:
        return False, "empty"
    if isinstance(val, str) and not val.strip():
        return False, "blank"
    # Summarize value
    if isinstance(val, list):
        return True, f"[{len(val)} items]"
    if isinstance(val, dict):
        keys = [k for k, v in val.items() if v]
        return True, f"{{{', '.join(keys)}}}"
    snippet = str(val)[:60].replace("\n", " ")
    return True, snippet


def run_test(target: dict) -> bool:
    print(f"\n{'='*60}")
    print(f"Library : {target['library']}")
    print(f"URL     : {target['url']}")
    print(f"{'='*60}")

    component = extract_component(target["url"], target["library"])
    if not component:
        print("  FAIL  — extraction returned None (scrape or LLM error)")
        return False

    # Required fields
    all_ok = True
    print("\n  Required fields:")
    for field in REQUIRED_FIELDS:
        ok, summary = check_field(component, field)
        status = "OK  " if ok else "MISS"
        if not ok:
            all_ok = False
        print(f"    [{status}] {field:<30} {summary}")

    # Rich schema fields
    print("\n  Rich schema fields:")
    populated = 0
    for field in RICH_FIELDS:
        ok, summary = check_field(component, field)
        status = "OK  " if ok else "----"
        if ok:
            populated += 1
        print(f"    [{status}] {field:<30} {summary}")

    # Library-specific expected fields
    print("\n  Library-expected fields:")
    for field in target["expected_fields"]:
        ok, summary = check_field(component, field)
        status = "OK  " if ok else "MISS"
        if not ok:
            all_ok = False
        print(f"    [{status}] {field:<30} {summary}")

    score = populated / len(RICH_FIELDS) * 100
    print(f"\n  Rich field coverage: {populated}/{len(RICH_FIELDS)} ({score:.0f}%)")
    if score < 50:
        print("  NOTE: Low coverage may indicate lazy-loaded code tabs (requires Playwright interaction)")

    # Dump compact JSON for inspection
    print("\n  Full schema (compact):")
    compact = {k: v for k, v in component.items() if k not in ("tsx_code", "raw_docs", "code_blocks")}
    print("  " + json.dumps(compact, indent=2, default=str).replace("\n", "\n  "))

    return all_ok


def main():
    print("Weave Scraping Pipeline — Integration Test")
    print(f"Testing {len(TARGETS)} libraries\n")

    if not os.environ.get("ANAKIN_API_KEY"):
        print("WARNING: ANAKIN_API_KEY not set — scraping will be disabled\n")

    results = []
    for target in TARGETS:
        try:
            ok = run_test(target)
            results.append((target["library"], ok))
        except Exception as exc:
            print(f"  ERROR — {exc}")
            results.append((target["library"], False))

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for _, ok in results if ok)
    for lib, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {lib}")
    print(f"\n{passed}/{len(results)} passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
