from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import subprocess
import os


def initialize_driver():
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

    chrome_options = Options()
    chrome_options.debugger_address = "localhost:9222"
    driver = wd.Chrome(options=chrome_options)
    return driver

def tear_down(driver):
    # Close browser and quit driver
    driver.close()
    driver.quit()

def data_frame_setup():
    return pd.DataFrame(columns=['Link', 'Job Title', 'Company', 'Location'])







#------------ NEEDS SEPARATE SCRIPT FOR CLEAN UP AND SAVING RAW AND PROCESSED DATA---------------------------#
# Data Clean up
df['Link'] = "https://www.indeed.com" + df['Link']

df = df.drop_duplicates(subset='Link', keep='first', ignore_index=True)

# Data clean up
df['Link'] = "https://www.indeed.com" + df['Link']
df = df.drop_duplicates(subset='Link', keep="first", ignore_index=True)

if os.path.exists("../data/processed/indeed_jobs.csv"):
    legacy_df = pd.read_csv("../data/processed/indeed_jobs.csv")
    jobs_to_email = df[~df['Link'].isin(legacy_df['Link'])].copy()
    jobs_to_email.to_excel("Jobs to Email.xlsx", sheet_name="New Jobs", index=False)
    df = pd.concat([df, legacy_df], ignore_index=True)
    # Data clean up
    df = df.drop_duplicates(subset='Link', keep="first", ignore_index=True)
else:
    df.to_excel("Jobs to Email.xlsx", sheet_name="New Jobs", index=False)

df.to_csv("indeed_jobs.csv", index=False)