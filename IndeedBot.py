from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd
import subprocess
import os


def build_df (df):
    verify_human = driver.find_elements(By.XPATH, "//h1[text()='Additional Verification Required']")

    if len(verify_human) > 0:
        input("Press enter once humanity is verified")

    # Data Clean up
    df['Link'] = "https://www.indeed.com" + df['Link']

    df = df.drop_duplicates(subset='Link', keep='first', ignore_index=True)

    rows = []

    # Loop to extract job data and navigate through pages
    while True:
        # Get the page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'lxml')
        boxes = soup.find_all('div', class_='job_seen_beacon')

        # Loop through each job listing
        for i in boxes:
            link = i.find('a').get('href')
            job_title = i.find('a', class_='jcs-JobTitle css-1baag51 eu4oa1w0').text
            company = i.find('span', attrs={'data-testid': 'company-name'}).text
            location = i.find('div', attrs={'data-testid': 'text-location'}).text

            # Append the extracted data to the rows list
            rows.append([link, job_title, company, location])

        # After the loop, convert rows to a DataFrame and append to the main df
        df_new = pd.DataFrame(rows, columns=['Link', 'Job Title', 'Company', 'Location'])
        df = pd.concat([df, df_new], ignore_index=True)

        # Find the "Next Page" button
        el = driver.find_elements(By.XPATH, '//a[@aria-label="Next Page"]')

        # If there is a next page, click it; otherwise, stop the loop
        if len(el) > 0:
            el[0].click()
            time.sleep(3)  # Wait for the next page to load
        else:
            break
    return df

# PowerShell command to start Chrome in remote debugging mode
subprocess.run([
    "powershell",
    "Start-Process",
    "chrome.exe",
    "-ArgumentList",
    "'--remote-debugging-port=9222', '--user-data-dir=C:\\Temp\\ChromeDebug'"
])

time.sleep(3)

# Set up the Chrome options
chrome_options = Options()
chrome_options.debugger_address = "localhost:9222"

# Initialize the Selenium WebDriver
driver = wd.Chrome(options=chrome_options)

scrum_master_remote = "https://www.indeed.com/jobs?q=scrum+master&l=Remote&fromage=1&from=searchOnDesktopSerp&vjk=e68d741ca4efde9a&filter=0"
business_analyst_remote = "https://www.indeed.com/jobs?q=business+analyst&l=Remote&fromage=1&from=searchOnDesktopSerp&vjk=16b12d0167bfaafe&filter=0"
scrum_master_katy = "https://www.indeed.com/jobs?q=scrum+master&l=Katy%2C+TX&fromage=1&radius=35&from=searchOnDesktopSerp&filter=0"
business_analyst_katy = "https://www.indeed.com/jobs?q=business+analyst&l=Katy%2C+TX&fromage=1&radius=35&from=searchOnDesktopSerp&filter=0"

job_urls = [
    scrum_master_remote,
    business_analyst_remote,
    business_analyst_katy,
    scrum_master_katy
]

df = pd.DataFrame(columns=['Link', 'Job Title', 'Company', 'Location'])

for url in job_urls:
    driver.get(url)
    df = pd.concat([df, build_df(df)], ignore_index=True)

# Data clean up
df['Link'] = "https://www.indeed.com" + df['Link']
df = df.drop_duplicates(subset='Link', keep="first", ignore_index=True)

if os.path.exists("indeed_jobs.csv"):
    legacy_df = pd.read_csv("indeed_jobs.csv")
    jobs_to_email = df[~df['Link'].isin(legacy_df['Link'])].copy()
    jobs_to_email.to_excel("Jobs to Email.xlsx", sheet_name="New Jobs", index=False)
    df = pd.concat([df, legacy_df], ignore_index=True)
    # Data clean up
    df = df.drop_duplicates(subset='Link', keep="first", ignore_index=True)
else:
    df.to_excel("Jobs to Email.xlsx", sheet_name="New Jobs", index=False)

df.to_csv("indeed_jobs.csv", index=False)

# Close browser and quit driver
driver.close()
driver.quit()
