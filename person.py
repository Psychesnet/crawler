#!/usr/bin/env python

# import numerical python library
import numpy
# import HTTP library
import requests
# import 表格 library
import pandas
# import time library
import datetime
import pickle

def crawl_person_report():
    stocks = []
    try:
        r = requests.get('https://tw.stock.yahoo.com/d/i/fgbuy_tse.html')
        html_df = pandas.read_html(r.text)[3].fillna("")
        for i in range(0, 30):
            stock = ''.join(c for c in html_df.iloc[i,1] if c.isdigit())
            if len(stock) == 4:
                stocks.append(stock)
    except Exception as e:
        return None
    return stocks

stocks_list = crawl_person_report()

with open ('stocks.txt', 'rb') as fp:
    items_list = pickle.load(fp)

merged_stocks_list = list(set(stocks_list) | set(items_list))

with open('stocks.txt', 'wb') as fp:
    pickle.dump(merged_stocks_list, fp)

print(merged_stocks_list)
