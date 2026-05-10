"""
Fixer — analyzes TypeScript build errors and auto-patches affected files using LLM.
"""
import json
import logging
import os
import re

from openai import OpenAI
from .ast_manager import apply_patch, _strip_fences

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def fix_errors(
    errors: list[dict],
    raw_output: str,
    sandbox_root: str,
    context_files: list[str] | None = None,
) -> dict:
    """
    Analyze TypeScript errors and generate + apply patches.

    Returns:
      {"patches": [{"file": ..., "applied": bool}], "success": bool}
    """
    if not errors:
        return {"patches": [], "success": True}

    # Collect unique files that have errors
    error_files = list({e["file"] for e in errors if e.get("file")})

    # Build file contents map for erroring files + any context files
    all_files = list({*error_files, *(context_files or [])})
    file_contents: dict[str, str] = {}
    for rel_path in all_files:
        abs_path = os.path.join(sandbox_root, rel_path)
        if os.path.isfile(abs_path):
            try:
                with open(abs_path, encoding="utf-8") as f:
                    file_contents[rel_path] = f.read()
            except Exception:
                pass

    if not file_contents:
        logger.warning("No readable files to fix")
        return {"patches": [], "success": False}

    # Construct a concise error summary for the LLM
    error_summary = "\n".join(
        f"{e['file']}:{e['line']}:{e['col']} {e['code']}: {e['message']}"
        for e in errors[:20]
    )

    files_block = "\n\n".join(
        f"### {path}\n```tsx\n{content[:4000]}\n```"
        for path, content in list(file_contents.items())[:4]
    )

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a TypeScript/Next.js build error fixer. "
                        "Given TypeScript compiler errors and the affected source files, "
                        "output a JSON object with key 'patches', an array of:\n"
                        '  {"file": "relative/path.tsx", "content": "<full corrected file content>"}\n'
                        "Rules:\n"
                        "- Fix ONLY the errors listed — do not refactor unrelated code\n"
                        "- Return the COMPLETE file content for each patched file\n"
                        "- Fix missing imports by adding them; fix type mismatches; "
                        "fix missing exports; resolve module-not-found errors\n"
                        "- If a utility like `cn` is missing, add a simple inline version\n"
                        "- Output valid JSON only"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"TypeScript errors:\n{error_summary}\n\n"
                        f"Source files:\n{files_block}"
                    ),
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        parsed = json.loads(response.choices[0].message.content or "{}")
        raw_patches = parsed.get("patches", [])

    except Exception as e:
        logger.error(f"LLM fix generation failed: {e}")
        return {"patches": [], "success": False}

    applied: list[dict] = []
    for patch in raw_patches:
        rel = patch.get("file", "").strip()
        content = patch.get("content", "")
        if not rel or not content:
            continue
        content = _strip_fences(content)
        abs_path = os.path.join(sandbox_root, rel)
        ok = apply_patch(abs_path, content)
        applied.append({"file": rel, "applied": ok})
        if ok:
            logger.info(f"Patched: {rel}")

    return {"patches": applied, "success": any(p["applied"] for p in applied)}


def fix_pasted_error(
    error_text: str,
    sandbox_root: str,
) -> dict:
    """
    Fix a runtime/build error pasted directly by the user.
    Reads the sandbox files mentioned in the stack trace and patches them.
    """
    # Extract file paths from the error text (Next.js/Node stack trace format)
    mentioned = re.findall(
        r'(?:at |in |\./)?((?:app|pages|components|lib|hooks)/[^\s:()]+\.(?:tsx?|jsx?))',
        error_text,
    )
    # Also grab bare filenames
    mentioned += re.findall(r'\b([\w/-]+\.(?:tsx?|jsx?))\b', error_text)
    context_files = list(dict.fromkeys(mentioned))[:6]

    # Build synthetic error dicts from the pasted text
    errors = []
    for m in re.finditer(
        r'(?P<file>[^\s]+\.tsx?)\s*[:(](?P<line>\d+)(?:[,:](?P<col>\d+))?\)?:?\s*(?P<msg>.+)',
        error_text,
    ):
        errors.append({
            "file": m.group("file"),
            "line": int(m.group("line")),
            "col": int(m.group("col") or "1"),
            "severity": "error",
            "code": "runtime",
            "message": m.group("msg").strip(),
        })

    # Fallback: treat the whole pasted text as the error description
    if not errors:
        errors = [{"file": "", "line": 0, "col": 0, "severity": "error", "code": "runtime", "message": error_text[:500]}]

    # Read context files
    file_contents: dict[str, str] = {}
    for rel in context_files:
        abs_path = os.path.join(sandbox_root, rel)
        if os.path.isfile(abs_path):
            try:
                with open(abs_path, encoding="utf-8") as f:
                    file_contents[rel] = f.read()
            except Exception:
                pass

    if not file_contents:
        # Read the main page as fallback
        page = os.path.join(sandbox_root, "app", "page.tsx")
        if os.path.isfile(page):
            with open(page, encoding="utf-8") as f:
                file_contents["app/page.tsx"] = f.read()

    files_block = "\n\n".join(
        f"### {p}\n```tsx\n{c[:4000]}\n```"
        for p, c in list(file_contents.items())[:4]
    )

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Next.js error fixer. Given a runtime/build error and the "
                        "relevant source files, output a JSON object with key 'patches':\n"
                        '  [{"file": "relative/path.tsx", "content": "<full corrected file>"}]\n'
                        "Fix the error minimally. Return complete file content. Output valid JSON only."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Error:\n{error_text[:2000]}\n\nFiles:\n{files_block}",
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        parsed = json.loads(response.choices[0].message.content or "{}")
        raw_patches = parsed.get("patches", [])
    except Exception as e:
        logger.error(f"fix_pasted_error LLM failed: {e}")
        return {"patches": [], "success": False}

    applied: list[dict] = []
    for patch in raw_patches:
        rel = patch.get("file", "").strip()
        content = _strip_fences(patch.get("content", ""))
        if not rel or not content:
            continue
        abs_path = os.path.join(sandbox_root, rel)
        ok = apply_patch(abs_path, content)
        applied.append({"file": rel, "applied": ok})

    return {"patches": applied, "success": any(p["applied"] for p in applied)}
