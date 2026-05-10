"""
Extraction Agent — extracts component code, deps, and metadata from a page.

Input:  component URL
Output: structured component data (name, tsx, deps, install, description)
"""
import logging
import json
import os
import hashlib

from openai import OpenAI
from tools.scraper import scrape_url

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def extract_component(url: str, library_name: str = "") -> dict | None:
    """
    Scrape a component page and extract structured component data.

    Returns dict with keys:
      id, name, source_library, source_url, component_type,
      description, dependencies, install_command, tsx_code, raw_docs
    """
    logger.info(f"Extracting component from {url}")

    # Step 1: Scrape the page (use browser for JS-heavy sites)
    page = scrape_url(url, use_browser=True)
    if not page or not page.get("markdown"):
        logger.warning(f"Failed to scrape {url}")
        return None

    markdown = page["markdown"]

    # Step 2: Use LLM to extract structured component data
    extracted = _extract_with_llm(url, markdown, library_name)
    if not extracted:
        return None

    # Step 3: Generate deterministic ID
    component_name = extracted.get("name", "unknown")
    component_id = hashlib.sha256(f"{library_name}:{component_name}:{url}".encode()).hexdigest()[:16]
    extracted["id"] = component_id
    extracted["source_url"] = url
    extracted["source_library"] = library_name
    extracted["raw_docs"] = markdown[:5000]  # Store first 5k chars of raw docs

    # Store raw markdown in storage/raw/
    _save_raw(component_id, markdown)

    return extracted


def _extract_with_llm(url: str, markdown: str, library_name: str) -> dict | None:
    """Use OpenAI to extract component data from page markdown."""
    # Truncate markdown to fit context window
    truncated = markdown[:8000]

    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a frontend component extractor. Given the markdown content "
                        "of a UI component library page, extract the component information. "
                        "Return a JSON object with these fields:\n"
                        '- "name": component name (e.g. "Animated Hero")\n'
                        '- "component_type": semantic type (hero, navbar, footer, card, button, etc.)\n'
                        '- "description": 1-2 sentence description\n'
                        '- "tsx_code": the main TSX/JSX code block (the component implementation)\n'
                        '- "dependencies": array of npm package dependencies\n'
                        '- "install_command": the npm/pnpm install command if shown\n'
                        "If a field is not found, use null. "
                        "For tsx_code, extract the MOST COMPLETE code block shown on the page."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Library: {library_name}\n"
                        f"URL: {url}\n\n"
                        f"Page content:\n{truncated}"
                    ),
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        return json.loads(content)

    except Exception as e:
        logger.error(f"LLM extraction failed for {url}: {e}")
        return None


def _save_raw(component_id: str, markdown: str):
    """Save raw markdown to storage/raw/."""
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    filepath = os.path.join(raw_dir, f"{component_id}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)
