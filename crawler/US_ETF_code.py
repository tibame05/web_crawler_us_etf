from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv

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
for c in etf_codes:
    print(c)

# 寫入 CSV 檔案
with open("us_etf_codes.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["ETF代碼"])  # 寫入欄位名稱
    for code in etf_codes:
        writer.writerow([code])

print("已成功寫入 us_etf_codes.csv")



# 取前三碼英文函式
def get_first_three_letters(code):
    letters = ''.join([ch for ch in code if ch.isalpha()])  # 過濾出英文字母
    return letters[:3].upper()  # 取前三個字母並轉大寫

# 修改你的主要程式碼片段，把 etf_codes 轉成前三碼英文
etf_codes_short = [get_first_three_letters(code) for code in etf_codes]

# 寫入 CSV 時，把 etf_codes_short 寫入
with open("us_etf_codes_short.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["ETF前三碼英文"])  # 欄位名稱
    for short_code in etf_codes_short:
        writer.writerow([short_code])

print("已成功寫入 us_etf_codes_short.csv")
