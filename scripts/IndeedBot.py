from job_search.core import initialize_driver, tear_down, data_frame_setup
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

SM_REMOTE = "https://www.indeed.com/jobs?q=scrum+master&l=Remote&fromage=1&from=searchOnDesktopSerp&vjk=e68d741ca4efde9a&filter=0"
BA_REMOTE = "https://www.indeed.com/jobs?q=business+analyst&l=Remote&fromage=1&from=searchOnDesktopSerp&vjk=16b12d0167bfaafe&filter=0"
SM_TX = "https://www.indeed.com/jobs?q=scrum+master&l=Katy%2C+TX&fromage=1&radius=35&from=searchOnDesktopSerp&filter=0"
BA_TX = "https://www.indeed.com/jobs?q=business+analyst&l=Katy%2C+TX&fromage=1&radius=35&from=searchOnDesktopSerp&filter=0"



class IndeedBot:
    def __init__(self):
        self.job_urls = [SM_REMOTE, BA_REMOTE, SM_TX, BA_TX]
        self.driver = None
        self.df = None

    def initialize_script(self):
        self.driver = initialize_driver()
        self.df = data_frame_setup()

    def end_driver(self):
        tear_down(self.driver)

    def job_search(self):
        for url in self.job_urls:
            self.driver.get(url)
            self.df = pd.concat([self.df, self.build_df(self.df)], ignore_index=True)


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
            df_new = pd.DataFrame(rows, columns=['Link', 'Job Title', 'Company', 'Location'])
            self.df = pd.concat([df, df_new], ignore_index=True)

            # Find the "Next Page" button
            el = self.driver.find_elements(By.XPATH, '//a[@aria-label="Next Page"]')

            # If there is a next page, click it; otherwise, stop the loop
            if len(el) > 0:
                el[0].click()
                time.sleep(3)  # Wait for the next page to load
            else:
                break












