import asyncio
import pandas as pd
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Go to website
        await page.goto("https://www.myshiptracking.com/")

        # Click "Vessel" tab
        await page.locator('//*[@id="myst-dropdown"]/ul/li[2]/a').click(timeout=60000) #60 seconds wait

        # Click "Search" button to open filters
        await page.locator('//*[@id="content_in_txt"]/div[2]/div/main/div[2]/div/div[2]/button[1]').click()

        # Fill in "Singapore" in search field
        await page.locator('//*[@id="pagefilter1"]').fill("Singapore")

        # Click actual "Search" button
        await page.locator('//*[@id="pagefilters-search"]').click()

        # Click to open "Fields" dropdown
        await page.locator('//*[@id="pagefilter_drpdn_fields"]/button').click()

        # Uncheck "MMSI"
        await page.locator('//*[@id="pagefilter_drpdn_fields"]/div/div[2]/label').click()

        # Uncheck "Speed"
        await page.locator('//*[@id="pagefilter_drpdn_fields"]/div/div[6]/label').click()

        # Uncheck "Received"
        await page.locator('//*[@id="pagefilter_drpdn_fields"]/div/div[10]/label').click()

        # Click "Refresh"
        await page.locator('//*[@id="pagefilter_drpdn_fields"]/div/div[12]/button').click()

        # Wait for table rows to appear
        await page.wait_for_selector('//*[@id="table-filter"]/tbody/tr')

        # Extract data
        rows = await page.locator('//*[@id="table-filter"]/tbody/tr').all()
        data = []

        for row in rows:
            columns = await row.locator('td').all()
            if len(columns) >= 4:
                vessel = (await columns[0].inner_text()).strip()
                type_ = (await columns[1].inner_text()).strip()
                area = (await columns[2].inner_text()).strip()
                destination = (await columns[3].inner_text()).strip()
                data.append([vessel, type_ , area, destination])

        # Save to CSV
        df = pd.DataFrame(data, columns=["Vessel", "Type", "Area", "Destination"])
        df.to_csv(r"C:\Users\pc\Desktop\Dev playground\RPA\PYTHON AUTOMATION\singapore vessel_playwright.csv", index=False)

        print("Successfully saved to CSV file")

        await browser.close()

# Run the Playwright script
asyncio.run(run())
