"""
Anakin-powered web scraping tools for Weave.

Uses the Anakin REST API (Path D from docs) with the existing poll pattern
from test.py. Falls back gracefully when ANAKIN_API_KEY is not set.
"""
import os
import time
import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.anakin.io/v1"
API_KEY = os.environ.get("ANAKIN_API_KEY", "")

_session = requests.Session()


def _ensure_session():
    """Lazy-init session headers."""
    if API_KEY:
        _session.headers.update({
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
        })


def _request(method: str, path: str, json_body=None, timeout: int = 30):
    """Make an HTTP request to the Anakin API."""
    _ensure_session()
    try:
        resp = _session.request(method, BASE_URL + path, json=json_body, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Anakin API error: {e}")
        return None


def _poll_job(job_id: str, endpoint: str = "/url-scraper", max_attempts: int = 60, interval: int = 3) -> dict | None:
    """Poll an async Anakin job until completed or failed."""
    for _ in range(max_attempts):
        result = _request("GET", f"{endpoint}/{job_id}")
        if result is None:
            time.sleep(interval)
            continue
        status = result.get("status", "")
        if status == "completed":
            return result
        if status == "failed":
            logger.error(f"Anakin job failed: {result.get('error')}")
            return None
        time.sleep(interval)
    logger.error("Anakin job timed out")
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scrape_url(url: str, use_browser: bool = False) -> dict | None:
    """
    Scrape a single URL and return markdown + metadata.
    Returns dict with keys: markdown, html, url, etc.
    Returns None on failure.
    """
    if not API_KEY:
        logger.warning("ANAKIN_API_KEY not set — scraping disabled")
        return None

    body = {"url": url}
    if use_browser:
        body["useBrowser"] = True

    submitted = _request("POST", "/url-scraper", body)
    if not submitted or "jobId" not in submitted:
        return None

    return _poll_job(submitted["jobId"])


def scrape_with_json(url: str, use_browser: bool = True) -> dict | None:
    """Scrape a URL and extract structured JSON via AI."""
    if not API_KEY:
        return None

    body = {"url": url, "generateJson": True}
    if use_browser:
        body["useBrowser"] = True

    submitted = _request("POST", "/url-scraper", body)
    if not submitted or "jobId" not in submitted:
        return None

    return _poll_job(submitted["jobId"])


def map_site(url: str) -> list[str]:
    """
    Discover all reachable URLs on a domain.
    Returns a list of URL strings.
    """
    if not API_KEY:
        return []

    submitted = _request("POST", "/map", {"url": url})
    if not submitted or "jobId" not in submitted:
        return []

    result = _poll_job(submitted["jobId"], endpoint="/map")
    if not result:
        return []

    # The map endpoint returns URLs in various possible fields
    urls = result.get("urls", [])
    if not urls:
        urls = result.get("links", [])
    return urls if isinstance(urls, list) else []


def search_web(query: str, limit: int = 5) -> list[dict]:
    """
    AI-powered web search (synchronous — no polling needed).
    Returns list of results with url, title, snippet.
    """
    if not API_KEY:
        return []

    result = _request("POST", "/search", {"prompt": query, "limit": limit})
    if not result:
        return []

    return result.get("results", result.get("citations", []))
