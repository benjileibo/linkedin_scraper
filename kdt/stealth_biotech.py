# pip3 install --user linkedin_scraper
# pip install webdriver-manager

from linkedin_scraper import Person, actions
from selenium import webdriver

driver = webdriver.Chrome(ChromeDriverManager().install())