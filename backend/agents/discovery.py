"""
Discovery Agent — discovers component pages on a UI library website.

Input:  library name + base URL
Output: list of component page URLs
"""
import logging
import json
import os
from urllib.parse import urlparse

from openai import OpenAI
from tools.scraper import map_site, scrape_url

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", ""))


def discover_components(library_name: str, base_url: str) -> list[str]:
    """
    Discover component page URLs for a given UI library.

    1. Try map_site() to get all URLs on the domain.
    2. Use LLM to filter down to actual component pages.
    3. Normalize, deduplicate, and return.
    """
    logger.info(f"Discovering components for {library_name} at {base_url}")

    # Step 1: Get all URLs from the site
    all_urls = map_site(base_url)
    logger.info(f"map_site returned {len(all_urls)} URLs")

    # If map returned nothing, try scraping the base URL for links
    if not all_urls:
        logger.info("map_site empty — falling back to scraping base URL")
        page = scrape_url(base_url, use_browser=True)
        if page and page.get("markdown"):
            all_urls = _extract_links_from_markdown(page["markdown"], base_url)
            logger.info(f"Extracted {len(all_urls)} links from base page")

    if not all_urls:
        logger.warning("No URLs discovered")
        return []

    # Step 2: Normalize URLs
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    normalized = set()
    for url in all_urls:
        if isinstance(url, str) and base_domain in url:
            normalized.add(url.split("#")[0].split("?")[0].rstrip("/"))
    all_urls = sorted(normalized)

    # Step 3: Use LLM to classify which URLs are component pages
    component_urls = _classify_urls(library_name, base_url, all_urls)
    logger.info(f"Classified {len(component_urls)} component URLs")

    return component_urls


def _extract_links_from_markdown(markdown: str, base_url: str) -> list[str]:
    """Extract URLs from markdown content."""
    import re
    parsed = urlparse(base_url)
    links = []
    # Match markdown links [text](url)
    for match in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', markdown):
        href = match.group(2)
        if href.startswith("/"):
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        if parsed.netloc in href:
            links.append(href)
    return links


def _classify_urls(library_name: str, base_url: str, urls: list[str]) -> list[str]:
    """Use OpenAI to classify which URLs are component pages."""
    if not urls:
        return []

    # Batch URLs into chunks of 100 to avoid token limits
    chunk_size = 100
    component_urls = []

    for i in range(0, len(urls), chunk_size):
        chunk = urls[i : i + chunk_size]
        url_list = "\n".join(f"- {u}" for u in chunk)

        try:
            response = client.chat.completions.create(
                model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a URL classifier for UI component libraries. "
                            "Given a list of URLs from a component library website, "
                            "identify which ones are individual component pages "
                            "(e.g. /components/button, /docs/hero-section). "
                            "Exclude: home pages, blog posts, changelog, pricing, "
                            "authentication pages, API references, generic docs pages. "
                            "Return ONLY a JSON array of the component page URLs."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Library: {library_name}\n"
                            f"Base URL: {base_url}\n\n"
                            f"URLs:\n{url_list}\n\n"
                            "Return a JSON array of component page URLs only."
                        ),
                    },
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            parsed = json.loads(content)
            # Handle both {"urls": [...]} and direct [...]
            if isinstance(parsed, list):
                component_urls.extend(parsed)
            elif isinstance(parsed, dict):
                component_urls.extend(parsed.get("urls", parsed.get("component_urls", [])))

        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            # Fallback: include URLs with common component patterns
            for u in chunk:
                lower = u.lower()
                if any(p in lower for p in ["/components/", "/docs/components/", "/ui/", "/blocks/"]):
                    component_urls.append(u)

    return list(set(component_urls))
