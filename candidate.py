# -*- coding: utf-8 -*-

"""
Created on Sat Mar 11 17:11:09 2017
@author: ghosty
"""
import csv
import ast
import httplib2
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from datetime import timedelta

stockList = [\
        ['3380', '明泰'], \
        ['2230','台泥']\
        ]
ProfileTitle = ['股票代碼', '股票名稱', '產業類別', \
        '現金股利', '股票股利', '盈餘配股', '公積配股', \
        '成立時間', '上市(櫃)時間', \
        '營業毛利率', '營業利益率', '稅前淨利率', '資產報酬率', '股東權益報酬率', '每股淨值', \
        '前4季盈餘', '前3季盈餘', '前2季盈餘', '前1季盈餘', \
        '前4年盈餘', '前3年盈餘', '前2年盈餘', '前1年盈餘'
        ]

def getProfile(stockID,stockName):
    url = 'https://tw.stock.yahoo.com/d/s/company_'+stockID+'.html'
    conn = httplib2.Http(cache=None)
    headers = {'Content-type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'} #windows
        #'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'} #Linux
        'User-Agent':'Mozilla/5.0 (Android; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0'} #android phone
    resp, doc = conn.request(url, method='GET', body=None, headers=headers)
    #docStr = str(doc.decode('cp950'));
    soup = BeautifulSoup(doc, 'html.parser')
    try:
        table1 = soup.findAll(text='基 本 資 料')[0].parent.parent.parent
        table2 = soup.findAll(text='營業毛利率')[0].parent.parent.parent
        category = table1.select('tr')[1].select('td')[1].text.strip()
        cashshare = table1.select('tr')[1].select('td')[3].text.strip("元")
        stockshare = table1.select('tr')[2].select('td')[3].text.strip("元")
        earnshare = table1.select('tr')[3].select('td')[3].text.strip("元")
        remainshare = table1.select('tr')[4].select('td')[3].text.strip("元")
        setupDate = table1.select('tr')[2].select('td')[1].text.strip()
        #setupDate[0] = int(setupDate[0])+1911
        #setupDate=str(setupDate[0])+'/'+setupDate[1]+'/'+setupDate[2]
        onboardDate = table1.select('tr')[3].select('td')[1].text.strip()
        #onboardDate[0] = int(onboardDate[0])+1911
        #onboardDate = str(onboardDate[0])+'/'+onboardDate[1]+'/'+onboardDate[2]
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
        result = list([stockID, stockName, category , \
            cashshare, stockshare, earnshare, remainshare, \
            setupDate, onboardDate, \
            grossprofit, netprofit, taxprofit, rate, earn, netvalue, \
            bq4, bq3, bq2, bq1, \
            by4, by3, by2, by1 \
            ])
    except:
        result = [stockID, stockName, 'access fail']
    #print('result=',result)
    return result

#main
listProfile=[ProfileTitle]
for row in stockList:
#for row in stockList:
    result = getProfile(row[0],row[1])
    print(result)
    listProfile.append(result)
#break #test once
#save result
f = open("~/Desktop/candidate.csv","w")
w = csv.writer(f, lineterminator='\n')
w.writerows(listProfile)
f.close()
