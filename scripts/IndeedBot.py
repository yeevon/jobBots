from job_search.core import initialize_driver, tear_down, initialize_df
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

SM_REMOTE = "https://www.indeed.com/jobs?q=scrum+master&l=Remote&fromage=1&from=searchOnDesktopSerp&vjk=e68d741ca4efde9a&filter=0"
BA_REMOTE = "https://www.indeed.com/jobs?q=business+analyst&l=Remote&fromage=1&from=searchOnDesktopSerp&vjk=16b12d0167bfaafe&filter=0"
SM_TX = "https://www.indeed.com/jobs?q=scrum+master&l=Katy%2C+TX&fromage=1&radius=35&from=searchOnDesktopSerp&filter=0"
BA_TX = "https://www.indeed.com/jobs?q=business+analyst&l=Katy%2C+TX&fromage=1&radius=35&from=searchOnDesktopSerp&filter=0"



class IndeedBot:
    def __init__(self):
        self.job_urls = [SM_REMOTE, BA_REMOTE, SM_TX, BA_TX]
        self.driver = None
        self.df = initialize_df()

    def run(self):
        self.initialize_script()
        self.job_search()
        self.clean_data()
        self.final_output()
        self.end_driver()

    def initialize_script(self):
        self.driver = initialize_driver()

    def end_driver(self):
        tear_down(self.driver)

    def job_search(self):
        for url in self.job_urls:
            self.driver.get(url)
            self.df = pd.concat([self.df, self.build_df(self.df)], ignore_index=True)

    # Data Clean up
    def clean_data(self):
        # Fix links that have multiple 'https://www.indeed.com' prefixes
        self.df['Link'] = self.df['Link'].apply(
            lambda x: x.replace("https://www.indeed.com", "", 1) if isinstance(x, str) and x.count(
                "https://www.indeed.com") > 1 else x
        )

        # Add prefix to links that don't start with it
        self.df['Link'] = self.df['Link'].apply(
            lambda x: "https://www.indeed.com" + x if isinstance(x, str) and not x.startswith(
                "https://www.indeed.com") else x
        )

        # Drop duplicates by URL and by job metadata
        self.df = self.df.drop_duplicates(subset='Link', keep="first", ignore_index=True)
        self.df = self.df.drop_duplicates(subset=['Job Title', 'Company', 'Location'], keep="first", ignore_index=True)


    # combine exiting data with new data, clean and remove dupes
    # produce file outputs (csv, excel)
    def final_output(self):
        if os.path.exists("../data/processed/indeed_jobs.csv"):
            legacy_df = pd.read_csv("../data/processed/indeed_jobs.csv")

            self.df['Job_Combination'] = self.df['Job Title'] + self.df['Company'] + self.df['Location']
            legacy_df['Job_Combination'] = legacy_df['Job Title'] + legacy_df['Company'] + legacy_df['Location']
            jobs_to_email = self.df[~self.df['Job_Combination'].isin(legacy_df['Job_Combination'])].copy()
            jobs_to_email.to_excel("data/processed/Jobs to Email.xlsx", sheet_name="New Jobs", index=False)

            self.df = pd.concat([self.df, legacy_df], ignore_index=True)
            self.clean_data()
        else:
            self.df.to_excel("data/processed/Jobs to Email.xlsx", sheet_name="New Jobs", index=False)

        # Create/Update csv db
        self.df.to_csv("data/processed/indeed_jobs.csv", index=False)

    def build_df (self, df):
        verify_human = self.driver.find_elements(By.XPATH, "//h1[text()='Additional Verification Required']")

        if len(verify_human) > 0:
            input("Press enter once humanity is verified")

        rows = []

        # Loop to extract job data and navigate through pages
        while True:
            # Get the page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
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
            df_new = initialize_df(rows)
            self.df = pd.concat([df, df_new], ignore_index=True)

            # Find the "Next Page" button
            el = self.driver.find_elements(By.XPATH, '//a[@aria-label="Next Page"]')

            # If there is a next page, click it; otherwise, stop the loop
            if len(el) > 0:
                el[0].click()
                time.sleep(3)  # Wait for the next page to load
            else:
                break












