from playwright.async_api import async_playwright


async def screenshot_components(url):

    async with async_playwright() as p:

        browser = await p.chromium.launch()

        page = await browser.new_page()

        await page.goto(url)

        await page.wait_for_load_state("networkidle")

        sections = page.locator("section")

        count = await sections.count()

        screenshots = []
        skipped = []

        print("\n" + "="*60)
        print("SCREENSHOT CAPTURE")
        print("="*60)
        print(f"URL: {url}")
        print(f"Total sections found: {count}\n")

        for i in range(count):

            try:

                section = sections.nth(i)

                # check visibility
                visible = await section.is_visible()

                if not visible:
                    skipped.append({
                        "index": i,
                        "reason": "not_visible"
                    })
                    continue

                # check bounding box
                box = await section.bounding_box()

                if not box:
                    skipped.append({
                        "index": i,
                        "reason": "no_bounding_box"
                    })
                    continue

                if box["height"] < 100:
                    skipped.append({
                        "index": i,
                        "reason": f"too_small ({box['height']}px)"
                    })
                    continue

                path = f"data/screenshots/section_{i}.png"

                await section.screenshot(
                    path=path,
                    timeout=5000
                )

                screenshots.append({
                    "index": i,
                    "path": path,
                    "size": box
                })

                print(f"✓ Section {i}: saved to {path} ({box['width']}x{box['height']}px)")

            except Exception as e:

                skipped.append({
                    "index": i,
                    "reason": str(e)
                })
                print(f"✗ Section {i}: {e}")

        await browser.close()

        print("\n" + "="*60)
        print(f"SUMMARY: {len(screenshots)} captured, {len(skipped)} skipped")
        print("="*60 + "\n")

        return {
            "url": url,
            "total_sections": count,
            "screenshots": screenshots,
            "skipped": skipped,
            "success": len(screenshots) > 0
        }