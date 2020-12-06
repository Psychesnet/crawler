#!/usr/bin/env python

# import numerical python library
import numpy
# import HTTP library
import requests
# import 表格 library
import pandas
# import time library
import datetime

BalanceSheet = "https://mops.twse.com.tw/mops/web/ajax_t164sb03";  # 資產負債表
ProfitAndLose = "https://mops.twse.com.tw/mops/web/ajax_t164sb04";  # 綜合損益表
CashFlowStatement = "https://mops.twse.com.tw/mops/web/ajax_t164sb05";  # 現金流量表
EquityStatement = "https://mops.twse.com.tw/mops/web/ajax_t164sb06"; # 權益變動表

def crawl_financial_report(url, stock_number, year, season):
    # encodeURIComponent=1&step=1&firstin=1&off=1&co_id=3056&year=109&season=3
    try:
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
        html_df = pandas.read_html(r.text)[1].fillna("")
    except Exception as e:
        return None
    return html_df

def which_season():
    # get the current day of the year
    doy = datetime.date.today().timetuple().tm_yday

    # "day of year" ranges for the northern hemisphere
    one = range(0, 90)
    two = range(91, 180)
    three = range(181, 240)
    # winter = everything else

    if doy in one:
        ret = 1
    elif doy in two:
        ret = 2
    elif doy in three:
        ret = 3
    else:
        ret = 4
    return ret

def which_year():
    year = datetime.datetime.now().year
    return year-1911

def loop():
    count = 20
    year = which_year()
    season = which_season()
    while count > 0:
        for s in range(season, 0, -1):
            print("{}:{}".format(year, s))
            count = count - 1
        year = year - 1
        seasion = 4

year = 99
season = 3
stock = 3056
data = crawl_financial_report(BalanceSheet, stock, year, season)
# 權益總額
# TotalEquity = 54
# 流動資產
# CurrentAssets = 10
# 流動負債
# CurrentLiabilities = 31
# 存貨
# Inventory = 8
# 負債總額
# TotalLiabilities = 39
# 長期借款
# LongTermLoan = 34
# 應付票據
# NotesPayable = 25

data = crawl_financial_report(ProfitAndLose, stock, year, season)
# 營業毛利
# GrossProfit = 3
# 營業收入
# GrossRevenue = 0
# 營業淨利(利益)
# OperatingIncome = 8
# 淨利
# NetIncome = 19
# 利息收入
# InterestIncome = 10
# 營業成本
# COST = 1

data = crawl_financial_report(CashFlowStatement, stock, year, season)
# 營業活動之淨現金流入（流出）
# CASHO = 34
# 投資活動之淨現金流入（流出）
# CASHI = 47
# 處分不動產、廠房及設備
# PFA = 42
# 取得不動產、廠房及設備
# SFA = 41
