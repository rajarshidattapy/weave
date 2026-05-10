#!/usr/bin/env python3
"""
One-shot script to backfill tags/styles/embedding_text for components
that were indexed before the metadata bug fix (None tsx_code crash).
"""
import os, sys, json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from database.models import get_all_components, _get_connection, JSON_FIELDS
from agents.metadata import generate_metadata


def update_component_tags(component_id: str, tags: list, styles: list, embedding_text: str):
    conn = _get_connection()
    conn.execute(
        "UPDATE components SET tags=?, styles=?, embedding_text=? WHERE id=?",
        (json.dumps(tags), json.dumps(styles), embedding_text, component_id),
    )
    conn.commit()
    conn.close()


def main():
    comps = get_all_components(limit=1000)
    needs_patch = [c for c in comps if not c.get("tags")]
    print(f"Components with empty tags: {len(needs_patch)}")

    updated = 0
    for c in needs_patch:
        name = c.get("name", "")
        tsx_code = c.get("tsx_code") or ""
        description = c.get("description") or ""

        meta = generate_metadata(name, tsx_code, description)
        if meta.get("tags") or meta.get("styles"):
            update_component_tags(
                c["id"],
                meta.get("tags", []),
                meta.get("styles", []),
                meta.get("embedding_text", f"{name}. {description}"),
            )
            updated += 1
            print(f"  Patched: {name} -> {meta['tags'][:5]}")
        else:
            print(f"  No tags generated for: {name}")

    print(f"\nDone. Updated {updated}/{len(needs_patch)} components.")


if __name__ == "__main__":
    main()
