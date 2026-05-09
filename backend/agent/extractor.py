"""
HTML parsing and content extraction utilities.
"""

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Set


def extract_component_links(html: str, base_url: str) -> List[str]:
    """
    Extract all component page URLs from the index page.
    
    Args:
        html: HTML content of the index page
        base_url: Base URL to resolve relative links
        
    Returns:
        List of unique full component URLs
    """
    soup = BeautifulSoup(html, "lxml")
    
    component_urls: Set[str] = set()
    
    # Find all links pointing to /docs/components/
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        
        if href and "/docs/components/" in href:
            full_url = urljoin(base_url, href)
            
            # Filter out invalid URLs
            if urlparse(full_url).netloc:
                component_urls.add(full_url)
    
    return sorted(list(component_urls))


def extract_code_blocks(html: str) -> List[str]:
    """
    Extract all code blocks from component page.
    
    Args:
        html: HTML content
        
    Returns:
        List of code block strings
    """
    soup = BeautifulSoup(html, "lxml")
    
    code_blocks = []
    
    for pre in soup.find_all("pre"):
        code = pre.find("code")
        if code:
            text = code.get_text()
            if text.strip():
                code_blocks.append(text.strip())
    
    return code_blocks


def extract_component_name(url: str) -> str:
    """
    Extract component name from URL.
    
    Args:
        url: Component page URL
        
    Returns:
        Component name (e.g., "button" from "/docs/components/button")
    """
    path = urlparse(url).path
    parts = path.split("/")
    
    if "components" in parts:
        idx = parts.index("components")
        if idx + 1 < len(parts):
            return parts[idx + 1].lower()
    
    return "unknown"
