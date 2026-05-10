"""
Injection Agent — injects components into the test-next sandbox.
"""
import logging
import os
import re
import subprocess
import json as json_mod

from database.models import get_component

logger = logging.getLogger(__name__)
SANDBOX_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "test-next")
)


def inject_component(component_id: str, target_file: str = "app/page.tsx") -> dict:
    component = get_component(component_id)
    if not component:
        return {"success": False, "modified_files": [], "installed_deps": [], "error": "Component not found"}

    tsx_code = component.get("tsx_code")
    if not tsx_code:
        return {"success": False, "modified_files": [], "installed_deps": [], "error": "No TSX code"}

    name = component.get("name", "Component")
    safe_name = re.sub(r'[^a-zA-Z0-9]', '', "".join(w.capitalize() for w in name.split()))
    modified_files, installed_deps = [], []

    try:
        # Write component file
        comp_dir = os.path.join(SANDBOX_ROOT, "app", "components")
        os.makedirs(comp_dir, exist_ok=True)
        filepath = os.path.join(comp_dir, f"{safe_name}.tsx")
        if "export" not in tsx_code:
            tsx_code = f"export default function {safe_name}() {{\n  return (\n{tsx_code}\n  );\n}}"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(tsx_code)
        modified_files.append(f"app/components/{safe_name}.tsx")

        # Inject import + JSX into target
        target_path = os.path.join(SANDBOX_ROOT, target_file)
        if os.path.exists(target_path) and os.path.abspath(target_path).startswith(os.path.abspath(SANDBOX_ROOT)):
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
            import_line = f'import {safe_name} from "./components/{safe_name}";'
            if import_line not in content:
                lines = content.split("\n")
                last_imp = max((i for i, l in enumerate(lines) if l.strip().startswith("import ")), default=-1)
                lines.insert(last_imp + 1, import_line)
                content = "\n".join(lines)
            jsx_tag = f"<{safe_name} />"
            if jsx_tag not in content:
                content = re.sub(r'(</main>)', f'        {jsx_tag}\n      \\1', content, count=1)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            modified_files.append(target_file)

        # Install deps
        deps = component.get("dependencies", [])
        if deps and isinstance(deps, list):
            pkg_path = os.path.join(SANDBOX_ROOT, "package.json")
            existing = set()
            if os.path.exists(pkg_path):
                with open(pkg_path) as f:
                    pkg = json_mod.load(f)
                    existing = set(pkg.get("dependencies", {}).keys()) | set(pkg.get("devDependencies", {}).keys())
            new_deps = [d for d in deps if isinstance(d, str) and d not in existing and re.match(r'^@?[a-z0-9][\w\-./]*$', d)]
            if new_deps:
                subprocess.run(["npm", "install", "--save"] + new_deps, cwd=SANDBOX_ROOT, timeout=120, check=True, capture_output=True)
                installed_deps = new_deps

        return {"success": True, "modified_files": modified_files, "installed_deps": installed_deps, "error": None}
    except Exception as e:
        return {"success": False, "modified_files": modified_files, "installed_deps": installed_deps, "error": str(e)}
