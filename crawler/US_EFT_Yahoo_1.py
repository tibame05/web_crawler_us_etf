import os
import pandas as pd
import yfinance as yf
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
with open("Output/us_etf_codes.csv", mode="w", newline="", encoding="utf-8") as file:
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
print(etf_codes)

ticker = etf_codes_short
start_date = '2015-05-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

failed_tickers = []

for r in ticker:
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
    