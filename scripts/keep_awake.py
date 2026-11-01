"""Mở Emerald Ship định kỳ để Streamlit Cloud (miễn phí) không cho app 'ngủ'.
Nếu app đã ngủ, tự bấm nút đánh thức."""
import asyncio
from playwright.async_api import async_playwright

APP_URL = "https://shipcontrol-ten42qbuu3mmnpbffqtfnl.streamlit.app/"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(APP_URL, timeout=120_000)
        await page.wait_for_timeout(8_000)
        wake = page.get_by_role("button", name="Yes, get this app back up!")
        if await wake.count():
            print("App was asleep - waking it up")
            await wake.first.click()
            await page.wait_for_timeout(90_000)
        else:
            print("App is awake")
        await browser.close()

asyncio.run(main())
