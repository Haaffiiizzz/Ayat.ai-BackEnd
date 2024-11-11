import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#     'Accept-Language': 'en-US,en;q=0.9',
#     'Accept-Encoding': 'gzip, deflate, br',
#     'Connection': 'keep-alive',
# }
# page = requests.get("https://quran411.com/", headers=headers)
# print(page.content)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get("https://quran411.com/")
page = driver.page_source
time.sleep(2)
soup = BeautifulSoup(page, "html.parser")

container = soup.find('div', class_ = "container")

listItems = container.find_all("li")

for i in listItems:
    print(i.text)