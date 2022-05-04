# pip3 install --user linkedin_scraper
# pip install webdriver-manager

from bs4 import BeautifulSoup as bs
import gspread
import datetime
from faker import Faker
from faker.providers.person.en import Provider
from linkedin_scraper import Person, actions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import pandas as pd
import re
import time 

# Parameters
spreadsheet_id = '1JoTlVppneyMvHXTnEMpWswPFifeuCXSlzxhbGVezdxQ'
worksheet_id = 915809190

# Get next available row
def next_available_row(worksheet):
    str_list = list(filter(None, worksheet.col_values(1)))
    return str(len(str_list))

# Pull linkedin credentials
creds = pd.read_csv('../creds.csv')
email = creds.loc[creds.key == 'username',"value"].values[0]
password = creds.loc[creds.key == 'password',"value"].values[0]

gc = gspread.service_account(filename='/Users/benleibowitz/Downloads/trusty-sentinel-348204-ef2d96a570ec.json')
sh = gc.open_by_key(spreadsheet_id).get_worksheet_by_id(worksheet_id)
last_row = int(next_available_row(sh))

# Login to LinkedIn
driver = webdriver.Chrome(ChromeDriverManager().install())
profile_driver = webdriver.Chrome(ChromeDriverManager().install())
actions.login(driver, email, password)
actions.login(profile_driver, email, password)

# Search for keyword
keywords = ["stealth biotech founder"]
wait_time = 5

for keyword in keywords:
    
    time.sleep(wait_time)
    driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/input').send_keys(keyword)
    driver.find_element_by_xpath('//*[@id="global-nav-typeahead"]/input').send_keys(Keys.RETURN)
    time.sleep(wait_time)

    expand_url = re.findall('https://(.*?)CLUSTER_EXPANSION', driver.page_source)[0] + "CLUSTER_EXPANSION"
    driver.get("http://" + expand_url)

    while True:

        # Scroll to bottom
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        time.sleep(wait_time)  
        
        # # Get only the unqiue profiles of interest
        html = driver.page_source
        profiles = re.findall('https://www.linkedin.com/in/.*?(?=\?miniProfile)', driver.page_source)
        
        for profile in profiles: 
            if profiles.count(profile) < 2: 
                profiles.remove(profile)

        # Remove duplicate profiles
        profiles = list(set(profiles))
        gsheet_profiles = sh.col_values(4)
        profiles = [profile for profile in profiles if profile not in gsheet_profiles]

        # Update google sheet with latest round of profile data
        for profile in profiles:
            last_row += 1
            profile_driver.get(profile)
            soup = bs(profile_driver.page_source, 'lxml')

            # Find name / location / title div
            name_div = soup.find('div', {'class':'mt2 relative'})
            
            # Name
            try:
                name = name_div.find_all('h1')[0].get_text().strip()
                first = name.split(' ')[0]
                last = name.split(' ')[1]
                sh.update(f'A{last_row}', first)
                sh.update(f'B{last_row}', last)
                sh.update(f'C{last_row}', name)
            except: pass
            time.sleep(wait_time)

            # Profile
            sh.update(f'D{last_row}', profile)

            # Title
            try:
                title = name_div.find('div', {'class':'text-body-medium break-words'}).get_text().strip()
                sh.update(f'E{last_row}', title)
            except: pass
            time.sleep(wait_time)

            # Location
            try:
                location = name_div.find('span', {'class':'text-body-small inline t-black--light break-words'}).get_text().strip()
                sh.update(f'F{last_row}', location)
            except: pass
            time.sleep(wait_time)

            # Current company
            try:
                company = name_div.find('div', {'class':'inline-show-more-text inline-show-more-text--is-collapsed inline-show-more-text--is-collapsed-with-line-clamp inline'}).get_text().strip()
                sh.update(f'G{last_row}', company)
            except: pass
            time.sleep(wait_time)

            # About section
            try:
                about = soup.find('div', {'class':'inline-show-more-text inline-show-more-text--is-collapsed'}).find('span').get_text().strip()
                sh.update(f'H{last_row}', about)
            except: pass
            time.sleep(wait_time)

           # Date
            sh.update(f'I{last_row}', str(datetime.datetime.now()))
            time.sleep(wait_time)

        try:
            # Scroll to bottom
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(wait_time) 

            # Find next page button then click it
            str_index = re.search('aria-label="Next" id="ember', driver.page_source).end()
            ember = int(driver.page_source[str_index:str_index+3])
            driver.find_elements_by_xpath(f'//*[@id="ember{ember}"]')[0].click()
            time.sleep(wait_time)

        except:
            # Scroll to bottom
            html = driver.find_element_by_tag_name('html')
            html.send_keys(Keys.END)
            time.sleep(wait_time) 

            try:
                # Scroll to bottom
                html = driver.find_element_by_tag_name('html')
                html.send_keys(Keys.END)
                time.sleep(wait_time) 

                # Find next page button then click it (ember length = 3)
                str_index = re.search('aria-label="Next" id="ember', driver.page_source).end()
                ember = int(driver.page_source[str_index:str_index+3])
                driver.find_elements_by_xpath(f'//*[@id="ember{ember}"]')[0].click()
                time.sleep(wait_time)
                pass

            except:
                try:
                    # Scroll to bottom
                    html = driver.find_element_by_tag_name('html')
                    html.send_keys(Keys.END)
                    time.sleep(wait_time) 

                    # Find next page button then click it (ember length = 4)
                    ember = int(driver.page_source[str_index:str_index+4])
                    driver.find_elements_by_xpath(f'//*[@id="ember{ember}"]')[0].click()
                    time.sleep(wait_time)
                    pass

                except:
                    # Scroll to bottom
                    html = driver.find_element_by_tag_name('html')
                    html.send_keys(Keys.END)
                    time.sleep(wait_time) 
                    pass
