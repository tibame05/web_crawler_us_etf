from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import pandas as pd
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）

from crawler.config import MYSQL_ACCOUNT, MYSQL_HOST, MYSQL_PASSWORD, MYSQL_PORT
from crawler.worker import app


def upload_data_to_mysql_US_ETF_list(df: pd.DataFrame):
    # 定義資料庫連線字串（MySQL 資料庫）
    # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
    # 上傳到 mydb, 同學可切換成自己的 database
    address = f"mysql+pymysql://{MYSQL_ACCOUNT}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/mydb"

    # 建立 SQLAlchemy 引擎物件
    engine = create_engine(address)

    # 建立連線（可用於 Pandas、原生 SQL 操作）
    connect = engine.connect()

    df.to_sql(
        "US_ETF_List",
        con=connect,
        if_exists="append",
        index=False,
    )

# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def US_ETF_list(url):
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
    upload_data_to_mysql_US_ETF_list(etf_data)
