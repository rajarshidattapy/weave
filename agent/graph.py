"""
LangGraph-powered component indexing pipeline.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from crawler import crawl_page, crawl_pages_batch
from extractor import extract_component_links, extract_code_blocks, extract_component_name
from screenshot import screenshot_component
from metadata import generate_metadata
from storage import save_component, ensure_data_dirs
from models import Component, ComponentMetadata
from sources import SOURCES


class IndexerState(TypedDict):
    """State for the component indexing pipeline."""
    source: str
    index_url: str
    base_url: str
    index_html: str
    component_urls: list[str]
    current_url: str
    current_name: str
    current_html: str
    code_blocks: list[str]
    screenshot_path: Optional[str]
    metadata: Optional[ComponentMetadata]
    processed_count: int
    total_count: int


async def crawl_index_node(state: IndexerState) -> dict:
    """Crawl the component library index page."""
    print(f"\n{'='*60}")
    print(f"CRAWLING INDEX: {state['source'].upper()}")
    print(f"{'='*60}")
    print(f"URL: {state['index_url']}")
    
    html = await crawl_page(state['index_url'])
    
    if not html:
        print("✗ Failed to crawl index page")
        return {"index_html": ""}
    
    print("✓ Index page crawled")
    return {"index_html": html}


def extract_links_node(state: IndexerState) -> dict:
    """Extract component URLs from index."""
    print(f"\nExtracting component links...")
    
    urls = extract_component_links(state['index_html'], state['base_url'])
    
    print(f"✓ Found {len(urls)} components")
    for i, url in enumerate(urls[:5], 1):
        print(f"  {i}. {url}")
    if len(urls) > 5:
        print(f"  ... and {len(urls) - 5} more")
    
    return {
        "component_urls": urls,
        "total_count": len(urls),
        "processed_count": 0
    }


async def process_component_node(state: IndexerState) -> dict:
    """Process a single component."""
    if state['processed_count'] >= len(state['component_urls']):
        return {"current_url": ""}
    
    url = state['component_urls'][state['processed_count']]
    name = extract_component_name(url)
    
    print(f"\n[{state['processed_count'] + 1}/{state['total_count']}] {name.upper()}")
    print(f"URL: {url}")
    
    # Crawl component page
    html = await crawl_page(url)
    
    if not html:
        print("  ✗ Failed to crawl component page")
        return {
            "current_url": "",
            "processed_count": state['processed_count'] + 1
        }
    
    # Extract code blocks
    code_blocks = extract_code_blocks(html)
    print(f"  ✓ Found {len(code_blocks)} code blocks")
    
    return {
        "current_url": url,
        "current_name": name,
        "current_html": html,
        "code_blocks": code_blocks,
        "processed_count": state['processed_count'] + 1
    }


async def screenshot_node(state: IndexerState) -> dict:
    """Capture component screenshot."""
    if not state['current_url']:
        return {"screenshot_path": None}
    
    # Reuse existing page object from crawling
    from playwright.async_api import async_playwright
    from crawler import get_page
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await get_page(browser, state['current_url'])
            path = await screenshot_component(page, state['current_name'])
            await page.close()
            
            return {"screenshot_path": path}
            
        finally:
            await browser.close()


async def metadata_node(state: IndexerState) -> dict:
    """Generate component metadata."""
    if not state['current_url']:
        return {"metadata": None}
    
    metadata = await generate_metadata(
        state['current_name'],
        state['current_html'][:2000],
        state['code_blocks']
    )
    
    return {"metadata": metadata}


def save_node(state: IndexerState) -> dict:
    """Save component to database."""
    if not state['current_url']:
        return {}
    
    try:
        component = Component(
            id=state['current_name'],
            name=state['current_name'].title(),
            source=state['source'],
            url=state['current_url'],
            code=state['code_blocks'],
            screenshot=state['screenshot_path'],
            metadata=state['metadata']
        )
        
        save_component(component)
        
    except Exception as e:
        print(f"  ✗ Error saving component: {e}")
    
    return {}


def should_continue(state: IndexerState) -> str:
    """Determine if we should process more components."""
    if state['processed_count'] < len(state['component_urls']):
        return "process_component"
    return END


# Build graph
graph = StateGraph(IndexerState)

graph.add_node("crawl_index", crawl_index_node)
graph.add_node("extract_links", extract_links_node)
graph.add_node("process_component", process_component_node)
graph.add_node("screenshot", screenshot_node)
graph.add_node("metadata", metadata_node)
graph.add_node("save", save_node)

# Set flow
graph.set_entry_point("crawl_index")
graph.add_edge("crawl_index", "extract_links")
graph.add_edge("extract_links", "process_component")
graph.add_edge("process_component", "screenshot")
graph.add_edge("screenshot", "metadata")
graph.add_edge("metadata", "save")
graph.add_conditional_edges(
    "save",
    should_continue,
    {
        "process_component": "process_component",
        END: END
    }
)

app = graph.compile()
