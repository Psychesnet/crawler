# -*- coding: utf-8 -*-

import urllib
import pandas
import csv
import ast
import datetime
import requests
import sched
import time
import json
import sys
from bs4 import BeautifulSoup

titles = ['股票代碼', '股票名稱', '產業類別', \
        '當盤成交價','當盤成交量','累積成交量', \
        '高價(2.5%)', '合理價(5%)', '低價(10%)', \
        '現金股利', '股票股利', '盈餘配股', '公積配股', \
        '成立時間', '上市(櫃)時間', \
        '營業毛利率', '營業利益率', '稅前淨利率', '資產報酬率', '股東權益報酬率', '每股淨值', \
        '前4季盈餘', '前3季盈餘', '前2季盈餘', '前1季盈餘', \
        '前4年盈餘', '前3年盈餘', '前2年盈餘', '前1年盈餘', \
        '連結'
        ]

def check_float(var, multiple):
    try:
        return float(var) * multiple
    except ValueError:
        return 0;

def stock_crawler(stockID):
    #　query data
    query_url = "http://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=tse_"+stockID+".tw&json=1&delay=0"
    data = json.loads(urllib.request.urlopen(query_url).read())
    # 過濾出有用到的欄位
    columns = ['c','n','z','tv','v','o','h','l','y']
    df = pandas.DataFrame(data['msgArray'], columns=columns)
    df.columns = ['股票代號','公司簡稱','當盤成交價','當盤成交量','累積成交量','開盤價','最高價','最低價','昨收價']
    instance_list = (df['當盤成交價'].tolist()[0], df['當盤成交量'].tolist()[0], df['累積成交量'].tolist()[0])
    df = df[0:0]
    return instance_list;

def profile(stockID, stockName):
    url = 'https://tw.stock.yahoo.com/d/s/company_'+stockID+'.html'
    resp = urllib.request.urlopen(url)
    html = resp.read()
    soup = BeautifulSoup(html.decode('cp950','ignore').encode('utf-8'), features="lxml")
    try:
        table1 = soup.findAll(text='基 本 資 料')[0].parent.parent.parent
        table2 = soup.findAll(text='營業毛利率')[0].parent.parent.parent
        category = table1.select('tr')[1].select('td')[1].text.strip()
        cashshare = table1.select('tr')[1].select('td')[3].text.strip("元")
        stockshare = table1.select('tr')[2].select('td')[3].text.strip("元")
        earnshare = table1.select('tr')[3].select('td')[3].text.strip("元")
        remainshare = table1.select('tr')[4].select('td')[3].text.strip("元")
        setupDate = table1.select('tr')[2].select('td')[1].text.strip()
        onboardDate = table1.select('tr')[3].select('td')[1].text.strip()
        grossprofit = table2.select('tr')[1].select('td')[1].text.strip()
        netprofit = table2.select('tr')[2].select('td')[1].text.strip()
        taxprofit = table2.select('tr')[3].select('td')[1].text.strip()
        rate = table2.select('tr')[4].select('td')[1].text.strip()
        bq4 = table2.select('tr')[1].select('td')[3].text.strip().strip("元")
        bq3 = table2.select('tr')[2].select('td')[3].text.strip().strip("元")
        bq2 = table2.select('tr')[3].select('td')[3].text.strip().strip("元")
        bq1 = table2.select('tr')[4].select('td')[3].text.strip().strip("元")
        earn = table2.select('tr')[5].select('td')[1].text.strip()
        netvalue = table2.select('tr')[5].select('td')[2].text.strip("每股淨值:").strip().strip("元")
        by4 = table2.select('tr')[1].select('td')[5].text.strip().strip("元")
        by3 = table2.select('tr')[2].select('td')[5].text.strip().strip("元")
        by2 = table2.select('tr')[3].select('td')[5].text.strip().strip("元")
        by1 = table2.select('tr')[4].select('td')[5].text.strip().strip("元")
        instance_info = stock_crawler(stockID)
        result = list([stockID, stockName, category , \
            instance_info[0], instance_info[1], instance_info[2], \
            check_float(cashshare, 40), check_float(cashshare, 20), check_float(cashshare, 10), \
            cashshare, stockshare, earnshare, remainshare, \
            setupDate, onboardDate, \
            grossprofit, netprofit, taxprofit, rate, earn, netvalue, \
            bq4, bq3, bq2, bq1, \
            by4, by3, by2, by1, \
            'https://tw.stock.yahoo.com/d/s/company_'+stockID+'.html'
            ])
    except:
        result = [stockID, stockName, 'access fail']
    #print('result=',result)
    return result


def parse_and_save(candidate, name):
    candidate_list = [titles]
    for row in candidate:
        result = profile(row[0],row[1])
        print(result)
        candidate_list.append(result)

    #save result
    f = open(name+".csv","w")
    w = csv.writer(f, lineterminator='\n')
    w.writerows(candidate_list)
    f.close()
