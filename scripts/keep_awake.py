"""Mở Emerald Ship mỗi giờ để Streamlit Cloud (miễn phí) không cho app 'ngủ'.
Nếu app đã ngủ thì tự bấm nút đánh thức, rồi chờ tới khi app chạy lại hẳn."""
import asyncio
import sys
from playwright.async_api import async_playwright

APP_URL = "https://shipcontrol-ten42qbuu3mmnpbffqtfnl.streamlit.app/"
INNER_URL = APP_URL + "~/+/"          # mở thẳng app (tạo một phiên xem thật)
WAKE_TEXT = "Yes, get this app back up!"


async def app_ready(page, wait_s):
    """Chờ app Streamlit hiện ra (tìm khung chính của app)."""
    for _ in range(wait_s // 5):
        for frame in page.frames:
            try:
                if await frame.locator('[data-testid="stApp"]').count():
                    return True
            except Exception:
                pass
        await page.wait_for_timeout(5_000)
    return False


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(APP_URL, timeout=120_000)
        await page.wait_for_timeout(10_000)

        wake = page.get_by_role("button", name=WAKE_TEXT)
        if await wake.count():
            print("App was asleep - waking it up")
            await wake.first.click()
            ok = await app_ready(page, 240)
        else:
            ok = await app_ready(page, 90)
            print("App is awake" if ok else "App page loaded but app not seen yet")

        # Mở thêm trang app bên trong và ở lại 30 giây để Streamlit tính là có người dùng
        inner = await browser.new_page()
        try:
            await inner.goto(INNER_URL, timeout=120_000)
            ok = await app_ready(inner, 90) or ok
            await inner.wait_for_timeout(30_000)
        except Exception as e:
            print("Inner page error:", e)

        await browser.close()
        print("Result:", "UP" if ok else "NOT CONFIRMED")
        if not ok:
            sys.exit(1)               # báo đỏ trên GitHub để biết có vấn đề

asyncio.run(main())
