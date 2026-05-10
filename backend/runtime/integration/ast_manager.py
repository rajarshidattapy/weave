"""
AST Manager — modifies TypeScript/TSX files using LLM-based semantic editing.

Rather than brittle regex/string-replace, the LLM receives the full file content
and outputs the correctly modified version — preserving all existing logic,
formatting, and structure while making the requested change.
"""
import logging
import os
import re

from openai import OpenAI

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))

_SYSTEM = (
    "You are a TypeScript/TSX code editor with deep knowledge of React and Next.js. "
    "You receive a file's current content and a single, precise instruction. "
    "Output ONLY the modified file content — no markdown fences, no explanations, "
    "no commentary before or after. The output must be valid TypeScript/TSX that "
    "compiles without errors."
)


def _strip_fences(text: str) -> str:
    """Remove markdown code fences the model sometimes adds despite instructions."""
    text = text.strip()
    text = re.sub(r'^```(?:tsx?|jsx?|typescript|javascript)?\n?', '', text)
    text = re.sub(r'\n?```$', '', text)
    return text.strip()


def _llm_edit(content: str, instruction: str) -> str:
    """Core LLM edit: send file + instruction, get back modified file."""
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _SYSTEM},
                {
                    "role": "user",
                    "content": (
                        f"File content:\n{content}\n\n"
                        f"Instruction: {instruction}"
                    ),
                },
            ],
            temperature=0,
        )
        result = _strip_fences(response.choices[0].message.content or "")
        if not result or len(result) < 10:
            logger.warning("LLM returned empty/tiny file — keeping original")
            return content
        return result
    except Exception as e:
        logger.error(f"LLM edit failed: {e}")
        return content


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def add_import(file_path: str, import_statement: str) -> bool:
    """
    Add an import statement to a TypeScript file.
    No-ops if the import is already present.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.warning(f"File not found for import injection: {file_path}")
        return False

    # Idempotency check — extract the imported name/path
    if import_statement.strip() in content:
        return True

    modified = _llm_edit(
        content,
        f"Add the following import at the end of the existing import block, "
        f"keeping all other imports untouched:\n{import_statement}",
    )
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified)
        return True
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False


def inject_jsx(file_path: str, jsx_snippet: str, location: str) -> bool:
    """
    Inject a JSX element into a TSX file.
    No-ops if the component tag is already present in the file.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.warning(f"File not found for JSX injection: {file_path}")
        return False

    # Idempotency: extract component name from snippet e.g. <Button /> → Button
    m = re.match(r'<([A-Za-z][A-Za-z0-9]*)', jsx_snippet.strip())
    if m and f'<{m.group(1)}' in content:
        return True

    modified = _llm_edit(
        content,
        f"Add the following JSX element: {jsx_snippet}\n"
        f"Location: {location}\n"
        f"Do not modify any other JSX or logic. Preserve all existing elements.",
    )
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified)
        return True
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False


def modify_file(file_path: str, instruction: str) -> bool:
    """Apply an arbitrary instruction to a TypeScript/TSX file."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return False

    modified = _llm_edit(content, instruction)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(modified)
        return True
    except Exception as e:
        logger.error(f"Failed to write {file_path}: {e}")
        return False


def apply_patch(file_path: str, patched_content: str) -> bool:
    """Directly write pre-generated patched content to a file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(patched_content)
        return True
    except Exception as e:
        logger.error(f"Failed to write patch to {file_path}: {e}")
        return False
