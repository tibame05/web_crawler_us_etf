import os
import pandas as pd
import yfinance as yf

# 擴充為迴圈
# 美股六大ETF
ticker = ['SPY','VOO','IVV','VTI','QQQ','VT']
start_date = '2015-05-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

for r in ticker:
    df = yf.download(r, start=start_date, end=end_date)
    df = df.reset_index() # 把日期變成一般欄位
    df = df.drop(df.index[0])
    # csv_name = f"{r}.csv"
    csv_name = os.path.join('Output', f"{r}.csv")
    df.to_csv(csv_name, encoding="utf-8", index=False)