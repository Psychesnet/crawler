#!/usr/bin/env python3

from pandas_datareader import data
import matplotlib.pyplot as plt
import pandas as pd

dtw = data.DataReader("^TWII", "yahoo", "2000-01-01","2018-01-01")
d1102 = data.DataReader("1102.TW", "yahoo", "2000-01-01","2018-01-01")
plt.plot(d1102['Close'])
print(d1102['Close'])
plt.show()
