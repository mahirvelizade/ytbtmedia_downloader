import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

COOKIES_PATH = Path(__file__).parent.parent.parent / "cookies.txt"


async def refresh_cookies() -> bool:
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                    " AppleWebKit/537.36 (KHTML, like Gecko)"
                    " Chrome/131.0.0.0 Safari/537.36"
                ),
                locale="en-US",
            )
            page = await context.new_page()
            await page.goto("https://www.youtube.com", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(3)
            cookies = await context.cookies()
            await browser.close()

        netscape_lines = ["# Netscape HTTP Cookie File"]
        for c in cookies:
            domain = c.get("domain", "")
            flag = "TRUE" if domain.startswith(".") else "FALSE"
            path = c.get("path", "/")
            secure = "TRUE" if c.get("secure", False) else "FALSE"
            expires = str(int(c.get("expires", 0)))
            name = c.get("name", "")
            value = c.get("value", "")
            httponly = "TRUE" if c.get("httpOnly", False) else "FALSE"
            netscape_lines.append(
                f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
            )

        COOKIES_PATH.write_text("\n".join(netscape_lines), encoding="utf-8")
        logger.info(f"Cookies refreshed: {len(cookies)} cookies -> {COOKIES_PATH}")
        return True

    except Exception as e:
        logger.warning(f"Cookie refresh failed: {e}")
        return False
