import pandas as pd
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）

from crawler.config import MYSQL_ACCOUNT, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT
from crawler.worker import app


def upload_data_to_mysql_US_ETF_Yahoo_DPS(df: pd.DataFrame):
    # 定義資料庫連線字串（MySQL 資料庫）
    # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
    # 上傳到 mydb, 同學可切換成自己的 database
    address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/mydb"

    # 建立 SQLAlchemy 引擎物件
    engine = create_engine(address)

    # 建立連線（可用於 Pandas、原生 SQL 操作）
    connect = engine.connect()

    df.to_sql(
        "US_ETF_Yahoo_DPS",
        con=connect,
        if_exists="append",
        index=False,
    )


# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def US_ETF_Yahoo_DPS(tickers):

    for ticker in etf_codes:
        # 抓取配息資料
        dividends = yf.Ticker(ticker).dividends
        if not dividends.empty:
            dividends_df = dividends.reset_index()
            dividends_df.columns = ["date", "dividend_per_unit"]    # 調整欄位名稱
            dividends_df["date"] = dividends_df["date"].dt.date  # 只保留年月日
            dividends_df.insert(0, "etf_id", ticker)  # 新增股票代碼欄位，放第一欄
            dividends_df.insert(3, "currency", "USD")  # 新增欄位，放第一欄
            dividends_df.to_csv(f"{dividend_dir}/{ticker}_dividends.csv", index=False, encoding="utf-8-sig")
        else:
            print(f"{ticker} 沒有配息資料")     
    upload_data_to_mysql_US_ETF_Yahoo_DPS(dividends_df)