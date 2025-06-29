import yfinance as yf
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
        df = yf.download(r, start=start_date, end=end_date)
        
        if df.empty:
            print(f"[⚠️ 警告] 無法下載 {r} 的資料")
            failed_tickers.append(r)
            continue
        df.columns = df.columns.droplevel(1)  # 把 'Price' 這層拿掉
        df.reset_index(inplace=True)
    upload_data_to_mysql_US_ETF_Yahoo(df)