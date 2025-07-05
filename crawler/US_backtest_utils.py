import pandas as pd
import numpy as np
import pandas_ta as ta
import os
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.makedirs("Output/historical_price_data", exist_ok=True)

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
    
start_date = '2015-05-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

failed_tickers = []

for r in etf_codes:
    print(f"正在下載：{r}")
    try:
        df = yf.download(r, start=start_date, end=end_date, auto_adjust=False)
        df = df[df["Volume"] > 0].ffill()
        df.reset_index(inplace=True)
        df.rename(columns={
            "Date": "date",
            "Adj Close": "adj_close",
            "Close": "close",
            "High": "high",
            "Low": "low",
            "Open": "open",
            "Volume": "volume"
        }, inplace=True)
        if df.empty:
            raise ValueError("下載結果為空")
    except Exception as e:
        print(f"[⚠️ 錯誤] {r} 下載失敗：{e}")
        failed_tickers.append(r)
        continue
    df.columns = df.columns.droplevel(1)  # 把 'Price' 這層拿掉

    
    # RSI (14) (相對強弱指標)
    df["rsi"] = ta.rsi(df["close"], length=14)

    # MA5、MA20（移動平均線）（也可以使用 df['close'].rolling(5).mean())）
    df["ma5"] = ta.sma(df["close"], length=5)
    df["ma20"] = ta.sma(df["close"], length=20)

    # MACD（移動平均收斂背離指標）
    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df["macd_line"] = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["macd_hist"] = macd["MACDh_12_26_9"]

    # KD 指標（STOCH: 隨機震盪指標）
    stoch = ta.stoch(df["high"], df["low"], df["close"], k=14, d=3, smooth_k=3)
    df["pct_k"] = stoch["STOCHk_14_3_3"]
    df["pct_d"] = stoch["STOCHd_14_3_3"]

    # 增加該日報酬率與累積報酬指數
    df['daily_return'] = df['adj_close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).cumprod()
    df.insert(0, "etf_id", r)  # 新增一欄「etf_id」
    print (df)
    #df.columns = ["etf_id","date", "dividend_per_unit"]    # 調整欄位名稱
    columns_order = ['etf_id', 'date', 'adj_close','close','high', 'low', 'open','volume',
                     'rsi', 'ma5', 'ma20', 'macd_line', 'macd_signal', 'macd_hist',
                     'pct_k', 'pct_d', 'daily_return', 'cumulative_return']
    df = df[columns_order]
    # 儲存技術指標結果
    print("開始 2️⃣ 進行技術指標計算與績效分析")
    output_dir = "Output/output_with_indicators"              # 存儲含技術指標的結果
    os.makedirs(output_dir, exist_ok=True)
    csv_name = os.path.join(output_dir, f"{r}_with_indicators.csv")
    df.to_csv(csv_name, encoding="utf-8", index=False)



   