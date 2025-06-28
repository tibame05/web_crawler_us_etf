from crawler.tasks_US_EFT_Yahoo import US_EFT_Yahoo

etf_list = ['VOO']
# 發送到 twse 的 queue
for tickers in etf_list:
     US_EFT_Yahoo.s(tickers).apply_async(queue="twse")
     print("send US_EFT_Yahoo task ")
     
# 發送到 tpex 的 queue
etf_list_1 = ['SPY']
for tickers in etf_list_1:
     US_EFT_Yahoo.s(tickers).apply_async(queue="tpex")
     print("send US_EFT_Yahoo_1 task ")