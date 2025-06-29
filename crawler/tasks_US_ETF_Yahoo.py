import yfinance as yf
import os
import pandas as pd
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）

from crawler.config import MYSQL_ACCOUNT, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT
from crawler.worker import app


def upload_data_to_mysql_US_ETF_Yahoo(df: pd.DataFrame):
    # 定義資料庫連線字串（MySQL 資料庫）
    # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
    # 上傳到 mydb, 同學可切換成自己的 database
    address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/mydb"

    # 建立 SQLAlchemy 引擎物件
    engine = create_engine(address)

    # 建立連線（可用於 Pandas、原生 SQL 操作）
    connect = engine.connect()

    df.to_sql(
        "US_ETF_Price",
        con=connect,
        if_exists="append",
        index=False,
    )

# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def US_EFT_Yahoo(tickers):
    ticker = tickers
    start_date = '2015-05-01'
    end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    failed_tickers = []


    for r in ticker:
        print(f"正在下載：{r}")
        try:
            df = yf.download(r, start=start_date, end=end_date)
            if df.empty:
                raise ValueError("下載結果為空")
        except Exception as e:
            print(f"[⚠️ 錯誤] {r} 下載失敗：{e}")
            failed_tickers.append(r)
            continue
        df.columns = df.columns.droplevel(1)  # 把 'Price' 這層拿掉
        df.reset_index(inplace=True)

        # 新增一欄「Ticker」
        df.insert(0, "Stock_ID", r)

        csv_name = os.path.join('Output', f"{r}.csv")
        df.to_csv(csv_name, encoding="utf-8", index=False)
        print(f"[✅ 完成] 已儲存 {csv_name}")

        
    # 寫入失敗清單
    if failed_tickers:
        with open("Output/failed_downloads.txt", "w", encoding="utf-8") as f:
            for ft in failed_tickers:
                f.write(ft + "\n")
        print(f"[⚠️ 已記錄] 無法下載的代碼已寫入 Output/failed_downloads.txt")
    upload_data_to_mysql_US_ETF_Yahoo(df)