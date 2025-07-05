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
summary_df = [] 
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

    # 確保 date 欄位為 datetime
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"])

    # 回測期間
    backtest_start = df["date"].iloc[0].strftime("%Y-%m-%d")
    backtest_end = df["date"].iloc[-1].strftime("%Y-%m-%d")
    print(backtest_start, backtest_end)
    # 總報酬率（Total Return）
    # 增加該日報酬率與累積報酬指數
    df['daily_return'] = df['adj_close'].pct_change()
    df['cumulative_return'] = (1 + df['daily_return']).cumprod()
    total_return = df['cumulative_return'].iloc[-1] - 1

    # 年化報酬率（CAGR）
    days = (df["date"].iloc[-1] - df["date"].iloc[0]).days

    if days <= 0 or df['cumulative_return'].iloc[-1] <= 0:
        cagr = np.nan
    else:
        cagr = df['cumulative_return'].iloc[-1] ** (365 / days) - 1

    # 最大回撤（Max Drawdown）
    roll_max = df['cumulative_return'].cummax()
    drawdown = df['cumulative_return'] / roll_max - 1
    max_drawdown = drawdown.min()

    # 夏普比率（Sharpe Ratio）
    std_return = df['daily_return'].std()
    sharpe = np.sqrt(252) * df['daily_return'].mean() / std_return if std_return and std_return != 0 else np.nan
    
    
    summary_data = {
        "etf_id": r,
        "backtest_start": backtest_start,
        "backtest_end": backtest_end,
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe
        }

    summary_df.append(summary_data)

summary_df = pd.DataFrame(summary_df)
# 指定欄位輸出順序
desired_order = ["etf_id", "backtest_start", "backtest_end", "total_return", "cagr", "max_drawdown", "sharpe_ratio"]
summary_df = summary_df[desired_order]

performance_dir = "Output/output_backtesting_metrics"     # 儲存績效評估報表
os.makedirs(performance_dir, exist_ok=True)

summary_csv_path = os.path.join(performance_dir, "backtesting_performance_summary.csv")
summary_df.to_csv(summary_csv_path, index=False)

print("✅ 技術指標與績效分析完成")
