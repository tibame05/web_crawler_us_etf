# 匯入必要套件
import pandas as pd  # 用來處理資料表（DataFrame）
from loguru import logger  # 日誌工具，用來輸出 log 訊息
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）
from crawler.worker import app


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import pandas as pd
from sqlalchemy import create_engine  # 建立資料庫連線的工具（SQLAlchemy）



if __name__ == "__main__":
    # 定義資料庫連線字串（MySQL 資料庫）
    # 格式：mysql+pymysql://使用者:密碼@主機:port/資料庫名稱
    address = "mysql+pymysql://root:test@127.0.0.1:3306/mydb"

    # 建立 SQLAlchemy 引擎物件
    engine = create_engine(address)

    # 建立連線（可用於 Pandas、原生 SQL 操作）
    connect = engine.connect()

    # 建立一個空的 DataFrame 並加入一個欄位 column_1，內容是 0~9
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
    driver.quit()

    df = pd.DataFrame(etf_data, columns=['Stock_ID', 'ETF_Name'])

    # 將 DataFrame 上傳至 MySQL 資料庫中的 test_upload 資料表
    # if_exists="replace" 表示如果資料表已存在，將其覆蓋
    # index=False 表示不上傳索引欄位
    df.to_sql(
        "test_upload",
        con=connect,
        if_exists="replace",
        index=False,
    )

    # 上傳成功後，輸出 log 訊息
    logger.info("upload success")
