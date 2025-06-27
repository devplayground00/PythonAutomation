import os
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from contextlib import suppress
import tkinter as tk
from tkinter import filedialog, messagebox


#Subclass to prevent destructor error
class SafeChrome(uc.Chrome):
    def __del__(self):
        pass  # Prevent undetected_chromedriver from trying to quit again

url = "https://www.myshiptracking.com/"

def scrape_vessel_data(destination_keyword: str, timeout: int = 60):
    options = uc.ChromeOptions()
    driver = SafeChrome(options=options)
    driver.maximize_window()

    try:
        driver.get(url)

        WebDriverWait(driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="myst-dropdown"]/ul/li[2]/a'))
        ).click()

        WebDriverWait(driver, timeout).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//*[@id="content_in_txt"]/div[2]/div/main/div[2]/div/div[2]/button[1]'))
        ).click()

        WebDriverWait(driver, timeout).until(
            expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="pagefilter1"]'))
        ).send_keys(destination_keyword)

        WebDriverWait(driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="pagefilters-search"]'))
        ).click()

        WebDriverWait(driver, timeout).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="pagefilter_drpdn_fields"]/button'))
        ).click()

        # Uncheck some columns
        for checkbox_index in [2, 6, 10]:
            WebDriverWait(driver, timeout).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, f'//*[@id="pagefilter_drpdn_fields"]/div/div[{checkbox_index}]/label'))
            ).click()

        WebDriverWait(driver, timeout).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, '//*[@id="pagefilter_drpdn_fields"]/div/div[12]/button'))
        ).click()

        rows = WebDriverWait(driver, timeout).until(
            expected_conditions.presence_of_all_elements_located((By.XPATH, '//*[@id="table-filter"]/tbody/tr'))
        )

        data = []

        for row in rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            if len(columns) >= 4:
                vessel = columns[0].text.strip()
                vessel_type = columns[1].text.strip()
                area = columns[2].text.strip()
                destination = columns[3].text.strip()
                data.append([vessel, vessel_type, area, destination])

        return pd.DataFrame(data, columns=["Vessel", "Type", "Area", "Destination"])

    finally:
        with suppress(Exception):
            driver.quit()
            del driver


# GUI + Logic
def main():
    # Use tkinter to choose folder
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Choose Folder", "Please select a folder to save the vessel data.")
    base_path = filedialog.askdirectory(title="Select Output Folder")

    if not base_path:
        messagebox.showerror("Error", "No folder selected. Exiting.")
        return

    destinations = ["Singapore", "Malaysia", "Indonesia"]
    excel_output_path = os.path.join(base_path, "vessels_by_port.xlsx")
    all_data = {}

    for city in destinations:
        print(f"Scraping vessels for: {city}")
        df = scrape_vessel_data(city)
        safe_city = city.replace(" ", "_").lower()
        csv_path = os.path.join(base_path, f"{safe_city}_vessels.csv")

        df.to_csv(csv_path, index=False)
        print(f"Saved CSV for {city}: {csv_path}")
        all_data[city] = df

    with pd.ExcelWriter(excel_output_path) as writer:
        for city, df in all_data.items():
            df.to_excel(writer, sheet_name=city[:31], index=False)

    print(f"Excel file saved with all cities: {excel_output_path}")
    messagebox.showinfo("Done", f"Scraping complete.\nFiles saved to:\n{base_path}")

if __name__ == "__main__":
    main()