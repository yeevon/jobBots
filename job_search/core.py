from pandas import DataFrame
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import subprocess



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

def initialize_df(rows=None) -> DataFrame:
    return pd.DataFrame(rows or [], columns=['Link', 'Job Title', 'Company', 'Location'])

#------------ NEEDS SEPARATE SCRIPT FOR CLEAN UP AND SAVING RAW AND PROCESSED DATA---------------------------#


