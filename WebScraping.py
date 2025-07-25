import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://course.mytcas.com"

async def scrape_mytcas():

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False, 
        )
        page = await browser.new_page()

        await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(20000) 

if __name__ == "__main__":
    asyncio.run(scrape_mytcas())