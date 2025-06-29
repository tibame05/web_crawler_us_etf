from crawler.tasks_US_ETF_Yahoo import US_ETF_Yahoo
from crawler.tasks_US_ETF_list import US_ETF_list
from crawler.tasks_US_ETF_Yahoo_DPS  import US_ETF_Yahoo_DPS

etf_list = ['VOO']
# 發送到 twse 的 queue
for tickers in etf_list:
     US_ETF_Yahoo.s(tickers).apply_async(queue="twse")
     print("send US_ETF_Yahoo task ")
     
# 發送到 tpex 的 queue
etf_list_1 = ['SPY']
for tickers in etf_list_1:
     US_ETF_Yahoo_DPS.s(tickers).apply_async(queue="tpex")
     print("send US_ETF_Yahoo_DPS task ")

# 發送到 US_ETF_list 的 queue
url = "https://tw.tradingview.com/markets/etfs/funds-usa/"
US_ETF_list.s(url).apply_async(queue="US_ETF_list")
print("send US_ETF_list task ")     

