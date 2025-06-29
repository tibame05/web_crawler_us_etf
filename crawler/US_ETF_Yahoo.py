import pandas as pd
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os
import csv

os.makedirs("Output", exist_ok=True)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

url = "https://tw.tradingview.com/markets/etfs/funds-usa/"
driver.get(url)

# 等待表格載入
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

etf_data = []

# 逐列抓取
rows = soup.select("table tbody tr")
for row in rows:
    code_tag = row.select_one('a[href^="/symbols/"]')
    name_tag = row.select_one("sup")
    
    if code_tag and name_tag:
        code = code_tag.get_text(strip=True)
        name = name_tag.get_text(strip=True)
        etf_data.append((code, name))

driver.quit()

etf_codes = [code for code, _ in etf_data]
print("所有ETF代碼：")
    
start_date = '2015-05-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

failed_tickers = []

for r in etf_codes:
    print(f"正在下載：{r}")
    df = yf.download(r, start=start_date, end=end_date)
    
    if df.empty:
        print(f"[⚠️ 警告] 無法下載 {r} 的資料")
        failed_tickers.append(r)
        continue
    df.columns = df.columns.droplevel(1)  # 把 'Price' 這層拿掉
    
    df.reset_index(inplace=True)
    csv_name = os.path.join('Output', f"{r}.csv")
    df.to_csv(csv_name, encoding="utf-8", index=False)
    print(f"[✅ 完成] 已儲存 {csv_name}")

# 寫入失敗清單
if failed_tickers:
    with open("Output/failed_downloads.txt", "w", encoding="utf-8") as f:
        for ft in failed_tickers:
            f.write(ft + "\n")
    print(f"[⚠️ 已記錄] 無法下載的代碼已寫入 Output/failed_downloads.txt")
    