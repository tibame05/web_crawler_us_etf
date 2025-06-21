import pandas as pd
import requests

from crawler.worker import app


# 註冊 task, 有註冊的 task 才可以變成任務發送給 rabbitmq
@app.task()
def crawler_finmind(stock_id):
    url = "https://api.finmindtrade.com/api/v4/data"
    parameter = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": "2024-01-01",
        "end_date": "2025-06-17",
    }
    resp = requests.get(url, params=parameter)
    data = resp.json()
    if resp.status_code == 200:
        df = pd.DataFrame(data["data"])
        print(df)
        print("upload db")
    else:
        print(data["msg"])
