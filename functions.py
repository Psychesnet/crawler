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

titles = ['庫存', '股票代碼', '股票名稱', '產業類別', \
        '高價(2.5%)', '合理價(5%)', '低價(10%)', \
        '殖利率', '當盤成交價', \
        '現金股利', '股票股利', '盈餘配股', '公積配股', \
        '成立時間', '上市(櫃)時間', \
        '營業毛利率', '營業利益率', '稅前淨利率', '資產報酬率', '股東權益報酬率', '每股淨值', \
        '前4季盈餘', '前3季盈餘', '前2季盈餘', '前1季盈餘', \
        '前4年盈餘', '前3年盈餘', '前2年盈餘', '前1年盈餘', \
        '連結'
        ]

def check_float(var, multiple):
    try:
        return round(float(var) * multiple, 1)
    except ValueError:
        return 0;

def price(id):
    url = 'https://tw.stock.yahoo.com/q/q?s='+id
    try:
        page = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(page.decode('cp950','ignore').encode('utf-8'), features="lxml")
        table = soup.find_all(text='成交')[0].parent.parent.parent
        stock_name = table.select('tr')[1].select('td')[0].text
        price = table.select('tr')[1].select('td')[2].text
        #print(stock_name.strip('加到投資組合'))
        #print('成交價 :',price)
        return price
    except:
        print('股票代碼錯誤或查無此代碼!!')
        return 0

def percentage(stock_price, cash_share):
    return round(float(cash_share) * 100.0/float(stock_price), 2)

def profile(id, had):
    url = 'https://tw.stock.yahoo.com/d/s/company_'+id+'.html'
    resp = urllib.request.urlopen(url)
    html = resp.read()
    soup = BeautifulSoup(html.decode('cp950','ignore').encode('utf-8'), features="lxml")
    try:
        name = soup.title.string.split('-')[0]
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
        current_price = price(id)
        result = list([had, id, name, category , \
                check_float(cashshare, 40), check_float(cashshare, 20), check_float(cashshare, 10), \
                percentage(current_price, cashshare), current_price, \
                cashshare, stockshare, earnshare, remainshare, \
                setupDate, onboardDate, \
                grossprofit, netprofit, taxprofit, rate, earn, netvalue, \
                bq4, bq3, bq2, bq1, \
                by4, by3, by2, by1, \
                'https://tw.stock.yahoo.com/d/s/company_'+id+'.html'
                ])
    except:
        result = [id, name, 'access fail']
    #print('result=',result)
    return result


def parse_and_save(candidate, name):
    candidate_list = [titles]
    for row in candidate:
        result = profile(str(row[0]), row[1])
        print(result)
        candidate_list.append(result)

    #save result
    f = open(name+".csv","w+")
    w = csv.writer(f, lineterminator='\n')
    w.writerows(candidate_list)
    f.close()
