#!/usr/bin/env python

# import numerical python library
import numpy as np
# import HTTP library
import requests
# import 表格 library
import pandas as pd

BalanceSheet = "https://mops.twse.com.tw/mops/web/ajax_t164sb03";  # 資產負債表
ProfitAndLose = "https://mops.twse.com.tw/mops/web/ajax_t164sb04";  # 綜合損益表
CashFlowStatement = "https://mops.twse.com.tw/mops/web/ajax_t164sb05";  # 現金流量表
EquityStatement = "https://mops.twse.com.tw/mops/web/ajax_t164sb06"; # 權益變動表

def crawl_financial_report(url, stock_number, year, season):
    # encodeURIComponent=1&step=1&firstin=1&off=1&co_id=3056&year=109&season=3
    form_data = {
            'encodeURIComponent': 1,
            'step': 1,
            'firstin': 1,
            'off': 1,
            'co_id': stock_number,
            'year': year,
            'season': season,
            }

    r = requests.post(url, form_data)
    html_df = pd.read_html(r.text)[1].fillna("")
    return html_df


year = 109
season = 3
stock = 3056
# data = crawl_financial_report(BalanceSheet, stock, year, season)

# print('(1): 所有資料')
# print(data)
# TotalAssets = 21
# TotalEquity = 54
# CurrentAssets = 10
# CurrentLiabilities = 31
# Inventory = 8
# TotalLiabilities = 39
# LongTermLoan = 34
# NotesPayable = 25

# data = crawl_financial_report(ProfitAndLose, stock, year, season)

# print('(1): 所有資料')
# print(data)
# GrossProfit = 3
# GrossRevenue = 0
# OperatingIncome = 8
# NetIncome = 19
# InterestIncome=10
# COST = 1

data = crawl_financial_report(CashFlowStatement, stock, year, season)
CASHO = 34
CASHI = 47
PFA = 42
SFA = 41
