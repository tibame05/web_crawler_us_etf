from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")

# 自動下載對應版本的 chromedriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

url = "https://tcbbankfund.moneydj.com/etfweb/html/et081001.djhtm#CID=all"
driver.get(url)
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")
table = soup.find("table", {"class": "tblData"})

if table:
    rows = table.find_all("tr")[1:]
    for row in rows[:5]:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        print(cols)

driver.quit()