"""
Integration Planner — uses LLM to generate a structured plan for integrating
a component into the test-next sandbox.
"""
import json
import logging
import os

from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def generate_plan(
    component: dict,
    target_file: str = "app/page.tsx",
    existing_files: dict[str, str] | None = None,
) -> dict:
    """
    Generate a structured integration plan for a component.

    Returns:
    {
        "component_file": {"path": str, "content": str},
        "utility_files":  [{"path": str, "content": str}],
        "target_modifications": [
            {
                "path": str,
                "action": "add_import" | "inject_jsx" | "modify",
                "import_statement": str,   # for add_import
                "jsx_snippet": str,        # for inject_jsx
                "location": str,           # e.g. "as last child of <main>"
                "instruction": str,        # for modify
            }
        ],
        "dependencies": [str],
        "notes": str,
    }
    """
    name = component.get("name", "Component")
    description = component.get("description", "")
    tsx_code = (component.get("tsx_code") or "").strip()
    known_deps = component.get("dependencies") or []
    source_lib = component.get("source_library", "")

    if not tsx_code:
        return {"error": f"No TSX code available for {name}"}

    target_content = (existing_files or {}).get(target_file, "")

    prompt_user = (
        f"Component name: {name}\n"
        f"Source library: {source_lib}\n"
        f"Description: {description}\n"
        f"Known npm dependencies: {', '.join(known_deps) if known_deps else 'none'}\n\n"
        f"Component source code:\n```tsx\n{tsx_code[:5000]}\n```\n\n"
        f"Target file to inject into ({target_file}):\n```tsx\n{target_content[:2000]}\n```"
    )

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior Next.js/TypeScript engineer. "
                        "Given a UI component and its target file, output an integration plan as JSON.\n\n"
                        "JSON schema:\n"
                        "{\n"
                        '  "component_file": {"path": "app/components/Name.tsx", "content": "..."},\n'
                        '  "utility_files": [{"path": "lib/utils.ts", "content": "..."}],\n'
                        '  "target_modifications": [\n'
                        '    {"path": "app/page.tsx", "action": "add_import",\n'
                        '     "import_statement": "import Name from \'@/components/Name\';"},\n'
                        '    {"path": "app/page.tsx", "action": "inject_jsx",\n'
                        '     "jsx_snippet": "<Name />",\n'
                        '     "location": "as last child of <main>"}\n'
                        '  ],\n'
                        '  "dependencies": ["pkg-name"],\n'
                        '  "notes": "brief explanation"\n'
                        "}\n\n"
                        "Rules:\n"
                        "- component_file.content must be the COMPLETE runnable TSX file\n"
                        "- Fix the component code if it references utilities/icons not available "
                        "(replace with inline equivalents or remove dependencies)\n"
                        "- utility_files only if the component genuinely needs them (e.g. cn helper)\n"
                        "- import paths use '@/' alias (Next.js convention)\n"
                        "- dependencies: only packages NOT provided by the component source itself; "
                        "omit react, next, typescript\n"
                        "- Output valid JSON only — no markdown fences"
                    ),
                },
                {"role": "user", "content": prompt_user},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content or "{}")

    except Exception as e:
        logger.error(f"Plan generation failed for {name}: {e}")
        return {"error": str(e)}
