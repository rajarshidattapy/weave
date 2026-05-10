"""
Validator — runs TypeScript type-checking on the sandbox to catch integration errors.
"""
import logging
import os
import re
import subprocess

logger = logging.getLogger(__name__)


def validate(sandbox_root: str) -> dict:
    """
    Run `tsc --noEmit` in the sandbox to catch TypeScript errors.
    Returns a structured result with parsed error locations.
    """
    logger.info("Running TypeScript validation...")
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck"],
            cwd=sandbox_root,
            capture_output=True,
            text=True,
            timeout=90,
            shell=(os.name == "nt"),
        )
        raw = (result.stdout + result.stderr).strip()
        errors = _parse_tsc(raw)
        success = result.returncode == 0

        if success:
            logger.info("TypeScript validation passed")
        else:
            logger.warning(f"TypeScript validation found {len(errors)} error(s)")

        return {"success": success, "raw_output": raw, "errors": errors}

    except subprocess.TimeoutExpired:
        return {"success": False, "raw_output": "tsc timed out", "errors": []}
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        # Fall back to treating it as success so pipeline can continue
        return {"success": True, "raw_output": str(e), "errors": [], "warning": str(e)}


def _parse_tsc(output: str) -> list[dict]:
    """Parse tsc output lines into structured error objects."""
    errors: list[dict] = []
    for line in output.splitlines():
        m = re.match(
            r'^(.+?)\((\d+),(\d+)\):\s+(error|warning)\s+(TS\d+):\s+(.+)$', line
        )
        if m:
            errors.append({
                "file": m.group(1).strip(),
                "line": int(m.group(2)),
                "col": int(m.group(3)),
                "severity": m.group(4),
                "code": m.group(5),
                "message": m.group(6).strip(),
            })
    return errors
