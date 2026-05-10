"""
Dependency Manager — installs npm packages into the test-next sandbox.
"""
import json
import logging
import os
import re
import subprocess

logger = logging.getLogger(__name__)


def get_installed(sandbox_root: str) -> set[str]:
    pkg_path = os.path.join(sandbox_root, "package.json")
    if not os.path.exists(pkg_path):
        return set()
    with open(pkg_path, encoding="utf-8") as f:
        pkg = json.load(f)
    return (
        set(pkg.get("dependencies", {}).keys())
        | set(pkg.get("devDependencies", {}).keys())
    )


def install(deps: list[str], sandbox_root: str) -> dict:
    """Install missing npm packages. Returns result dict."""
    if not deps:
        return {"installed": [], "skipped": [], "success": True, "error": None}

    installed = get_installed(sandbox_root)
    to_install = [
        d for d in deps
        if d and d not in installed and re.match(r'^@?[\w\-./]+(@[\w\-.]+)?$', d)
    ]
    skipped = [d for d in deps if d not in to_install]

    if not to_install:
        return {"installed": [], "skipped": skipped, "success": True, "error": None}

    logger.info(f"Installing: {to_install}")
    try:
        result = subprocess.run(
            ["npm", "install", "--save"] + to_install,
            cwd=sandbox_root,
            capture_output=True,
            text=True,
            timeout=120,
            shell=(os.name == "nt"),
        )
        if result.returncode != 0:
            logger.warning(f"npm install error: {result.stderr[:500]}")
            return {
                "installed": [],
                "skipped": skipped,
                "success": False,
                "error": result.stderr[:500],
            }
        return {"installed": to_install, "skipped": skipped, "success": True, "error": None}
    except Exception as e:
        return {"installed": [], "skipped": skipped, "success": False, "error": str(e)}
