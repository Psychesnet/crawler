#!/usr/bin/env python3

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

stock_num = "2330"
stockNo = "{}.TW".format(stock_num)
startDate = "2020-08-01"
stock = yf.Ticker(stockNo)
stock_df = pd.DataFrame(stock.history(start=startDate))
stock_df = stock_df.reset_index()
print("參考交易日天數: {} 天".format(len(stock_df)))
stock_df.head()

stock_df['EMA_12'] = stock_df['Close'].ewm(span=12, adjust=False).mean()
stock_df['EMA_26'] = stock_df['Close'].ewm(span=26, adjust=False).mean()
stock_df['DIF'] = stock_df['EMA_12'] - stock_df['EMA_26']
stock_df['MACD'] = stock_df['DIF'].ewm(span=9, adjust=False).mean()
stock_df.head()

fig,ax1 = plt.subplots()
fig.set_size_inches(20, 6)
plt.title('MACD by Mr.HandByHand')
plt.xlabel('Date')
ax2 = ax1.twinx()
# macd & dif
ax1.set_ylabel('MACD', color='black')
ax1.plot(stock_df['Date'], stock_df['DIF'], color='gold', label="DIF", alpha=1)
ax1.plot(stock_df['Date'], stock_df['MACD'], color='coral', label="MACD", alpha=1)
ax1.legend(loc="lower left")
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(True)
# price
ax2.set_ylabel('Price', color='black')
ax2.plot(stock_df['Date'], stock_df['Close'], color='black', label="Price", linestyle=':', alpha=0.8)
# ma: 移動平均線(Moving Average)
stock_df['MA_7'] = stock_df['Close'].rolling(7).mean()
ax2.plot(stock_df['Date'], stock_df['MA_7'], color='blue', label="MA", linestyle='-', alpha=0.8)
ax2.legend(loc="upper left")
ax2.tick_params(axis='y', labelcolor='black')
fig.autofmt_xdate()
plt.show()
