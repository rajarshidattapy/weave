"""
Async web crawling utilities using Playwright.
"""

from playwright.async_api import async_playwright, Browser, Page


async def get_page(browser: Browser, url: str) -> Page:
    """
    Helper to get a new page with standard configuration.
    
    Args:
        browser: Playwright browser instance
        url: URL to navigate to
        
    Returns:
        Playwright Page object
    """
    page = await browser.new_page(
        viewport={"width": 1440, "height": 1200}
    )
    
    try:
        await page.goto(url, wait_until="networkidle", timeout=10000)
    except Exception as e:
        print(f"Warning: Navigation timeout for {url}: {e}")
    
    return page


async def crawl_page(url: str) -> str:
    """
    Crawl a single page and return its HTML.
    
    Args:
        url: URL to crawl
        
    Returns:
        HTML content as string
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        try:
            page = await get_page(browser, url)
            html = await page.content()
            await page.close()
            
            return html
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return ""
        
        finally:
            await browser.close()


async def crawl_pages_batch(urls: list[str]) -> dict[str, str]:
    """
    Crawl multiple pages in parallel for efficiency.
    
    Args:
        urls: List of URLs to crawl
        
    Returns:
        Dictionary mapping URL to HTML content
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        results = {}
        
        try:
            for url in urls:
                try:
                    page = await get_page(browser, url)
                    html = await page.content()
                    results[url] = html
                    await page.close()
                    
                except Exception as e:
                    print(f"Error crawling {url}: {e}")
                    results[url] = ""
            
            return results
            
        finally:
            await browser.close()