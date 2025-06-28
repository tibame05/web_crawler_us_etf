from crawler.tasks_US_EFT_Yahoo_1 import US_EFT_Yahoo_1

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# 設定 Chrome Driver (headless 模式)
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

url = "https://tw.tradingview.com/markets/etfs/funds-usa/"
driver.get(url)

time.sleep(5)  # 等待網頁及 JS 載入，必要時可調整秒數

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

# 找出表格列，抓第一欄 ETF 代碼
rows = soup.select("table tbody tr")
etf_codes = []
for row in rows:
    tds = row.find_all("td")
    if tds:
        code = tds[0].get_text(strip=True)
        etf_codes.append(code)

driver.quit()

print("抓到的美股ETF代碼：")
for stock_id in etf_codes:
    print(stock_id)

    US_EFT_Yahoo_1.delay(stock_id=stock_id)
