"""
Screenshot capture utilities for component previews.
"""

from playwright.async_api import Page
from pathlib import Path


async def screenshot_component(page: Page, component_name: str, output_dir: str = "data/screenshots") -> str | None:
    """
    Safely screenshot the main component preview area.
    
    Args:
        page: Playwright page object
        component_name: Name of component (for filename)
        output_dir: Directory to save screenshots
        
    Returns:
        Path to screenshot file, or None if failed
    """
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Try to find visible main content area
        main_locator = page.locator("main")
        
        if not await main_locator.count():
            print(f"  ⊘ No main content found for {component_name}")
            return None
        
        # Check if visible
        if not await main_locator.is_visible():
            print(f"  ⊘ Main content not visible for {component_name}")
            return None
        
        # Get bounding box
        box = await main_locator.bounding_box()
        
        if not box or box["height"] < 100:
            print(f"  ⊘ Component preview too small for {component_name}")
            return None
        
        # Take screenshot
        output_path = f"{output_dir}/{component_name}.png"
        
        await main_locator.screenshot(
            path=output_path,
            timeout=5000
        )
        
        print(f"  ✓ Screenshot: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"  ✗ Screenshot failed for {component_name}: {e}")
        return None
