#!/usr/bin/env python3

import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import talib

stock_num = "2330"
stockNo = "{}.TW".format(stock_num)
startDate = "2020-08-01"
stock = yf.Ticker(stockNo)
stock_df = pd.DataFrame(stock.history(start=startDate))
stock_df = stock_df.reset_index()
print("參考交易日天數: {} 天".format(len(stock_df)))
stock_df.head()

stock_df["MA7"] = talib.MA(stock_df['Close'], timeperiod=7)
stock_df["MA30"] = talib.MA(stock_df['Close'], timeperiod=30)
stock_df['MACD'], stock_df['MACD_Signal'], stock_df['MACD_Hist'] = talib.MACD(stock_df['Close'])
stock_df.head()

fig,ax1 = plt.subplots()
fig.set_size_inches(20, 6)
plt.title('MACD by Mr.HandByHand')
plt.xlabel('Date')
ax2 = ax1.twinx()
# macd & dif
ax1.set_ylabel('MACD', color='black')
ax1.plot(stock_df['Date'], stock_df['MACD'], color='yellow', label="MACD", alpha=2)
ax1.plot(stock_df['Date'], stock_df['MACD_Signal'], color='red', label="signal", alpha=2)
ax1.bar(stock_df['Date'], stock_df['MACD_Hist']*3, color='blue', label="hist")
ax1.legend(loc="lower left")
ax1.tick_params(axis='y', labelcolor='black')
ax1.grid(True)
# price
ax2.set_ylabel('Price', color='black')
ax2.plot(stock_df['Date'], stock_df['Close'], color='black', label="Price", linestyle=':', alpha=0.8)
# ma: 移動平均線(Moving Average)
ax2.plot(stock_df['Date'], stock_df['MA7'], color='purple', label="MA7", alpha=1, linestyle='-')
ax2.plot(stock_df['Date'], stock_df['MA30'], color='grey', label="MA30", alpha=1, linestyle='-')
ax2.legend(loc="upper left")
ax2.tick_params(axis='y', labelcolor='black')
fig.autofmt_xdate()
plt.show()
