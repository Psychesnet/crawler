#!/usr/bin/env python3

import os
import sys
import time
import numpy
import html
import requests
import datetime
import prettytable
import enum
import bs4
import matplotlib.pyplot as plt

BalanceSheet = "https://mops.twse.com.tw/mops/web/ajax_t164sb03";  # 資產負債表
ProfitAndLose = "https://mops.twse.com.tw/mops/web/ajax_t164sb04";  # 綜合損益表
CashFlowStatement = "https://mops.twse.com.tw/mops/web/ajax_t164sb05";  # 現金流量表
EquityStatement = "https://mops.twse.com.tw/mops/web/ajax_t164sb06"; # 權益變動表
Titles = ('代號', '股價', '產業類別', '每股淨值',
            '前1季盈餘', '前2季盈餘', '前3季盈餘',
            '前1年盈餘', '前2年盈餘', '前3年盈餘',
            '基本檢查項目', '現金流', '公司營運能力',
            '報酬率', '報投率', '本業收入比重',)

class Table(enum.Enum):
    YearSeason = 0
    Items = 1
    Charts = 2

class Items(enum.Enum):
    # from 資產負債表
    # 權益總額
    TotalEquity = 100
    # 流動資產
    CurrentAssets = 101
    # 流動負債
    CurrentLiabilities = 102
    # 存貨
    Inventory = 103
    # 負債總額
    TotalLiabilities = 104
    # 長期借款
    LongTermLoan = 105
    # 資產總額
    TotalAssets = 106
    # 普通股股本
    CommonStock = 107

    # from 綜合損益表
    # 營業毛利
    GrossProfit = 200
    # 營業收入
    GrossRevenue = 201
    # 營業利益
    OperatingIncome = 202
    # 稅後淨利
    NetIncome = 203
    # 利息收入
    InterestIncome = 204
    # 營業成本
    COST = 205
    # 稅前淨利
    NetIncomeBeforeTax = 206
    # 業外收入
    TotalNonOperatingRevenue = 207
    # 營業費用
    OperatingExpenses = 208
    # 每股盈餘 = 稅後淨利/總股數
    EPS = 209

    # from 現金流量表
    # 營業活動之淨現金流入（流出）
    CASHO = 300
    # 投資活動之淨現金流入（流出）
    CASHI = 301
    # 處分不動產、廠房及設備
    PFA = 302
    # 取得不動產、廠房及設備
    SFA = 303
    # 籌資活動之淨現金流入（流出）
    CAFA = 304
    # 發放現金股利
    CashDividends = 305

    # create by functions
    # 毛利率 = 營業毛利/營業收入(^)
    GrossMargin = 400
    # 負債權益比 = 負債總額/權益總額(v)
    DebtEquityRatio = 401
    # 流動比 = 流動資產/流動負債
    CurrentRatio = 402
    # 股東權益報酬率 = 淨利/權益總額
    ROE = 403
    # 營運費用率 = 營業費用/營業收入(v)
    OperatingExpenseRatio = 404
    # 淨利率 = 營業淨利/營業收入(^)
    ProfitMargin = 405
    # 資產報酬率 = 稅後淨利/平均總資產
    ROA = 406
    # 資產周轉率 = 營業收入/資產總額
    AssetTurnover = 407
    # 每股股利 = (權益總額+母公司業主（淨利∕損)/普通股股本
    DPS = 408
    # 股票配息率 = 每股股利÷每股盈餘(EPS)×100%
    PayoutRatio = 409


class StockHelper:
    index = 0
    stock_id = 0
    stock_name = ""
    stock_price = 0
    database = {}
    def __init__(self, index, id):
        self.index = index
        self.stock_id = id
        self.database[Table.YearSeason] = []
        self.database[Table.Items] = {}
        self.database[Table.Charts] = []

    def __repr__(self):
        return "stock"

    def __str__(self):
        return "ID: {0}".format(self.stock_id)

    def average(self, lst):
        return sum(lst) / len(lst)

    def item_with_average_norm(self, text, item, norm):
        return "{}({:.3f}):{}".format(text,
            self.average(self.database[Table.Items][item]), norm)

    def item_with_norm(self, text, norm):
        return "{}:{}".format(text, norm)

    def crawl_year_report(self):
        error_and_end = False
        count = 10
        year = self.which_year()
        season = 4
        if self.update_price_and_name():
            while count > 0:
                if self.update_balance_sheet(year, season):
                    self.database[Table.YearSeason].insert(0, "{0}.{1}".format(year, season))
                    self.update_profit_and_lose(year, season)
                    self.update_cash_flow(year, season)
                    # self.update_equity(year, season)
                    error_and_end = True
                else:
                    if error_and_end:
                        break
                year = year - 1
                count = count - 1

    def calcuate_and_save(self):
        print(self.stock_id)
        print("年度: {}".format(self.database[Table.YearSeason]))
        # 毛利率
        self.database[Table.Items].setdefault(Items.GrossMargin, [])
        for m, d in zip(self.database[Table.Items][Items.GrossProfit], self.database[Table.Items][Items.GrossRevenue]):
            if d == 0:
                self.database[Table.Items][Items.GrossMargin].append(float(0))
            else:
                self.database[Table.Items][Items.GrossMargin].append(float(m*100/d))
        # 負債權益比
        self.database[Table.Items].setdefault(Items.DebtEquityRatio, [])
        for m, d in zip(self.database[Table.Items][Items.TotalLiabilities], self.database[Table.Items][Items.TotalEquity]):
            if d == 0:
                self.database[Table.Items][Items.DebtEquityRatio].append(float(0))
            else:
                self.database[Table.Items][Items.DebtEquityRatio].append(float(m*100/d))
        # 流動比
        self.database[Table.Items].setdefault(Items.CurrentRatio, [])
        for m, d in zip(self.database[Table.Items][Items.CurrentAssets], self.database[Table.Items][Items.CurrentLiabilities]):
            if d == 0:
                self.database[Table.Items][Items.CurrentRatio].append(float(0))
            else:
                self.database[Table.Items][Items.CurrentRatio].append(float(m*100/d))
        # 股東權益報酬率
        self.database[Table.Items].setdefault(Items.ROE, [])
        for m, d in zip(self.database[Table.Items][Items.NetIncome], self.database[Table.Items][Items.TotalEquity]):
            if d == 0:
                self.database[Table.Items][Items.ROE].append(float(0))
            else:
                self.database[Table.Items][Items.ROE].append(float(m*100/d))
        # 負債權益比 vs 流動比 vs 股東權益報酬率
        png_name = "./{0}/DebtEquityRatioVSCurrentRatioVSROE.png".format(self.stock_id)
        self.draw_line(self.database[Table.YearSeason], "Year.Season",
                (self.database[Table.Items][Items.DebtEquityRatio],
                    self.database[Table.Items][Items.CurrentRatio],
                    self.database[Table.Items][Items.ROE]),
                (self.item_with_average_norm("負債權益比", Items.DebtEquityRatio, "< 50%"),
                    self.item_with_average_norm("流動比", Items.CurrentRatio, "> 150%"),
                    self.item_with_average_norm("股東權益報酬率", Items.ROE, ">= 8%")),
                "基本檢查項目", png_name)
        self.database[Table.Charts].append(self.create_img_table(png_name))
        print("負債權益比: {}".format(self.database[Table.Items][Items.DebtEquityRatio]))
        print("流動比: {}".format(self.database[Table.Items][Items.CurrentRatio]))
        print("股東權益報酬率 :{}".format(self.database[Table.Items][Items.ROE]))
        # 營業活動現金流 vs 淨利 vs 投資活動現金流 vs 融資活動現金流
        png_name = "./{0}/CASHOvsNetIncomeVsCASHIvsCAFA.png".format(self.stock_id)
        self.draw_bar(self.database[Table.YearSeason], "Year.Season",
                (self.database[Table.Items][Items.CASHO],
                    self.database[Table.Items][Items.NetIncome],
                    self.database[Table.Items][Items.CASHI],
                    self.database[Table.Items][Items.CAFA]),
                (self.item_with_norm("營業活動現金流", "正"),
                    self.item_with_norm("淨利", "正"),
                    self.item_with_norm("投資活動現金流", "負為投資資產"),
                    self.item_with_norm("融資活動現金流", "負為發放股利或還債")),
                "現金流", png_name)
        self.database[Table.Charts].append(self.create_img_table(png_name))
        print("營業活動現金流: {}".format(self.database[Table.Items][Items.CASHO]))
        print("淨利: {}".format(self.database[Table.Items][Items.NetIncome]))
        print("投資活動現金流: {}".format(self.database[Table.Items][Items.CASHI]))
        print("融資活動現金流: {}".format(self.database[Table.Items][Items.CAFA]))
        # 營業費用率
        self.database[Table.Items].setdefault(Items.OperatingExpenseRatio, [])
        for m, d in zip(self.database[Table.Items][Items.OperatingExpenses], self.database[Table.Items][Items.GrossRevenue]):
            if d == 0:
                self.database[Table.Items][Items.OperatingExpenseRatio].append(float(0))
            else:
                self.database[Table.Items][Items.OperatingExpenseRatio].append(float(m*100/d))
        # 淨利率
        self.database[Table.Items].setdefault(Items.ProfitMargin, [])
        for m, d in zip(self.database[Table.Items][Items.NetIncome], self.database[Table.Items][Items.GrossRevenue]):
            if d == 0:
                self.database[Table.Items][Items.ProfitMargin].append(float(0))
            else:
                self.database[Table.Items][Items.ProfitMargin].append(float(m*100/d))
        # 毛利率 vs 營業費用率 vs 淨利率
        png_name = "./{0}/GrossMarginVSOperatingIncomeVSNetIncome.png".format(self.stock_id)
        self.draw_line(self.database[Table.YearSeason], "Year.Season",
                (self.database[Table.Items][Items.GrossMargin],
                    self.database[Table.Items][Items.OperatingExpenseRatio],
                    self.database[Table.Items][Items.ProfitMargin]),
                (self.item_with_average_norm("毛利率", Items.GrossMargin, "^"),
                    self.item_with_average_norm("營業費用率", Items.OperatingExpenseRatio, "v"),
                    self.item_with_average_norm("淨利率", Items.ProfitMargin, "^")),
                "公司營運能力", png_name)
        self.database[Table.Charts].append(self.create_img_table(png_name))
        print("毛利率: {}".format(self.database[Table.Items][Items.GrossMargin]))
        print("營業費用率: {}".format(self.database[Table.Items][Items.OperatingExpenseRatio]))
        print("淨利率: {}".format(self.database[Table.Items][Items.ProfitMargin]))
        # 資產報酬率
        self.database[Table.Items].setdefault(Items.ROA, [])
        for m, d in zip(self.database[Table.Items][Items.NetIncome], self.database[Table.Items][Items.TotalAssets]):
            if d == 0:
                self.database[Table.Items][Items.ROA].append(float(0))
            else:
                self.database[Table.Items][Items.ROA].append(float(m*100/d))
        # 資產週轉率
        self.database[Table.Items].setdefault(Items.AssetTurnover, [])
        for m, d in zip(self.database[Table.Items][Items.GrossRevenue], self.database[Table.Items][Items.TotalAssets]):
            if d == 0:
                self.database[Table.Items][Items.AssetTurnover].append(float(0))
            else:
                self.database[Table.Items][Items.AssetTurnover].append(float(m*100/d))
        # 資產週轉率 vs 股東權益報酬率 vs 資產報酬率
        png_name = "./{0}/AssetTurnoverVsROEvsROA.png".format(self.stock_id)
        self.draw_line(self.database[Table.YearSeason], "Year.Season",
                (self.database[Table.Items][Items.AssetTurnover],
                    self.database[Table.Items][Items.ROE],
                    self.database[Table.Items][Items.ROA]),
                (self.item_with_average_norm("資產週轉率", Items.AssetTurnover, ""),
                    self.item_with_average_norm("股東權益報酬率", Items.ROE, ">= 8%"),
                    self.item_with_average_norm("資產報酬率", Items.ROA, "")),
                "報酬率", png_name)
        self.database[Table.Charts].append(self.create_img_table(png_name))
        print("資產週轉率: {}".format(self.database[Table.Items][Items.AssetTurnover]))
        print("股東權益報酬率: {}".format(self.database[Table.Items][Items.ROE]))
        print("資產報酬率: {}".format(self.database[Table.Items][Items.ROA]))
        # 每股股利
        self.database[Table.Items].setdefault(Items.DPS, [])
        for m, d in zip(self.database[Table.Items][Items.CashDividends], self.database[Table.Items][Items.CommonStock]):
            if d == 0:
                self.database[Table.Items][Items.DPS].append(float(0))
            else:
                self.database[Table.Items][Items.DPS].append(float(m*(-10)/d))
        # 股票配息率
        self.database[Table.Items].setdefault(Items.PayoutRatio, [])
        for m, d in zip(self.database[Table.Items][Items.DPS], self.database[Table.Items][Items.EPS]):
            if d == 0:
                self.database[Table.Items][Items.PayoutRatio].append(float(0))
            else:
                self.database[Table.Items][Items.PayoutRatio].append(float(m/d))
        # EPS vs 每股股利 vs 股票配息率
        png_name = "./{0}/EPSvsDPSvsPayoutRatio.png".format(self.stock_id)
        self.draw_bar(self.database[Table.YearSeason], "Year.Season",
                (self.database[Table.Items][Items.EPS],
                    self.database[Table.Items][Items.DPS]),
                (self.item_with_norm("每股盈餘", "^"),
                    self.item_with_norm("每股股利", "^")),
                "報酬率", png_name)
        self.database[Table.Charts].append(self.create_img_table(png_name))
        print("每股盈餘: {}".format(self.database[Table.Items][Items.EPS]))
        print("每股股利: {}".format(self.database[Table.Items][Items.DPS]))
        print("股票配息率: {}".format(self.database[Table.Items][Items.PayoutRatio]))
        # 營業收入 vs 業外收入 vs 稅前淨利
        png_name = "./{0}/GrossRevenueVSTotalNonOperatingRevenueVSNetIncomeBeforeTax.png".format(self.stock_id)
        self.draw_line(self.database[Table.YearSeason], "Year.Season",
                (self.database[Table.Items][Items.GrossRevenue],
                    self.database[Table.Items][Items.TotalNonOperatingRevenue],
                    self.database[Table.Items][Items.NetIncomeBeforeTax]),
                (self.item_with_norm("營業收入", "^"),
                    self.item_with_norm("業外收入", "v"),
                    self.item_with_norm("稅前淨利", "^")),
                "本業收入比重", png_name)
        self.database[Table.Charts].append(self.create_img_table(png_name))
        print("營業收入: {}".format(self.database[Table.Items][Items.GrossRevenue]))
        print("業外收入: {}".format(self.database[Table.Items][Items.TotalNonOperatingRevenue]))
        print("稅前淨利: {}".format(self.database[Table.Items][Items.NetIncomeBeforeTax]))

    def create_img_table(self, png):
        return '<img src=\"{}\" width=\"50%\" height=\"50%\">'.format(png)

    def dump_table(self, table):
        url = 'https://tw.stock.yahoo.com/d/s/company_{}.html'.format(self.stock_id)
        try:
            resp = requests.get(url)
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')
            table1 = soup.findAll(text='基 本 資 料')[0].parent.parent.parent
            table2 = soup.findAll(text='營業毛利率')[0].parent.parent.parent
            category = table1.select('tr')[1].select('td')[1].text.strip()
            bq1 = table2.select('tr')[1].select('td')[3].text.strip().strip("元")
            bq2 = table2.select('tr')[2].select('td')[3].text.strip().strip("元")
            bq3 = table2.select('tr')[3].select('td')[3].text.strip().strip("元")
            netvalue = table2.select('tr')[5].select('td')[2].text.strip("每股淨值:").strip().strip("元")
            by1 = table2.select('tr')[1].select('td')[5].text.strip().strip("元")
            by2 = table2.select('tr')[2].select('td')[5].text.strip().strip("元")
            by3 = table2.select('tr')[3].select('td')[5].text.strip().strip("元")
        except:
            print("fail to get the profile of {}".format(self.stock_id))

        current_data = [self.stock_name, self.stock_price,
            category, netvalue, bq1, bq2, bq3, by1, by2 ,by3]
        current_data.extend(self.database[Table.Charts])
        table.add_row(current_data)

    def update_price_and_name(self):
        url = 'https://tw.stock.yahoo.com/q/q?s={0}'.format(self.stock_id)
        try:
            page = requests.get(url)
            soup = bs4.BeautifulSoup(page.text, 'html.parser')
            table = soup.find_all(text='成交')[0].parent.parent.parent
            self.stock_name = table.select('tr')[1].select('td')[0].text.strip('加到投資組合')
            self.stock_price = table.select('tr')[1].select('td')[2].text
        except:
            print('股票代碼錯誤或查無此代碼!!')
            return False
        return True

    def draw_bar(self, x, xlabel, ys, ylabels, title, png_name):
        colors = ('#9999ff', '#ff9999', '#ffff99', '#99ffff', '#ff99ff')
        plt.figure(figsize=(7, 5))
        for i, (y, l) in enumerate(zip(ys, ylabels)):
            plt.bar(x, y, label=l,
                    facecolor=colors[i%len(colors)], edgecolor='white')
            # for tx, ty in zip(x, y):
                # plt.text(tx, ty, "{:.1f}".format(ty))
            plt.legend(loc='upper left')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel('Amount')
        # plt.show()
        plt.savefig(png_name, dpi=300)

    def draw_line(self, x, xlabel, ys, ylabels, title, png_name):
        colors = ('red', 'green', 'blue', 'yellow')
        plt.figure(figsize=(7, 5))
        for i, (y, l) in enumerate(zip(ys, ylabels)):
            line = plt.plot(x, y, label=l,
                    color=colors[i%len(colors)], linewidth=1.0)
            for tx, ty in zip(x, y):
                plt.text(tx, ty, "{:.1f}".format(ty))
            plt.setp(line, marker = "o")
            plt.legend(loc='upper left')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel('Amount')
        # plt.show()
        plt.savefig(png_name, dpi=300)

    def update_balance_sheet(self, year, season):
        key = "{0}.{1}".format(year, season)
        backup_folder = "./{0}/{1}".format(self.stock_id, key)
        os.makedirs(backup_folder, exist_ok = True)
        backup_file = "{0}/b.html".format(backup_folder)
        try:
            if not os.path.exists(backup_file):
                time.sleep(3);
                okay = self.crawl(backup_file, BalanceSheet, year, season)
                if not okay:
                    return False
            if os.path.exists(backup_file):
                con = open(backup_file, mode="r", encoding="UTF-8").read()
                soup = bs4.BeautifulSoup(con, 'html.parser')
                self.find_and_update_item(soup, '　權益總額', '　權益總計',
                        Table.Items, Items.TotalEquity)
                self.find_and_update_item(soup, '　　流動資產合計', None,
                        Table.Items, Items.CurrentAssets)
                self.find_and_update_item(soup, '　　流動負債合計', None,
                        Table.Items, Items.CurrentLiabilities)
                self.find_and_update_item(soup, '　　　存貨', None,
                        Table.Items, Items.Inventory)
                self.find_and_update_item(soup, '　負債總額', '　負債總計',
                        Table.Items, Items.TotalLiabilities)
                self.find_and_update_item(soup, '　　　長期借款', None,
                        Table.Items, Items.LongTermLoan)
                self.find_and_update_item(soup, '　資產總額', '　資產總計',
                        Table.Items, Items.TotalAssets)
                self.find_and_update_item(soup, '　　　普通股股本', '　　　　普通股股本',
                        Table.Items, Items.CommonStock)
        except Exception as e:
            print("{0} at update_balance_sheet".format(e))
            return False
        return True

    def update_profit_and_lose(self, year, season):
        key = "{0}.{1}".format(year, season)
        backup_folder = "./{0}/{1}".format(self.stock_id, key)
        os.makedirs(backup_folder, exist_ok = True)
        backup_file = "{0}/p.html".format(backup_folder)
        try:
            if not os.path.exists(backup_file):
                time.sleep(3);
                okay = self.crawl(backup_file, ProfitAndLose, year, season)
                if not okay:
                    return False
            if os.path.exists(backup_file):
                con = open(backup_file, mode="r", encoding="UTF-8").read()
                soup = bs4.BeautifulSoup(con, 'html.parser')
                self.find_and_update_item(soup, '營業毛利（毛損）淨額', None,
                        Table.Items, Items.GrossProfit)
                self.find_and_update_item(soup, '營業收入合計', None,
                        Table.Items, Items.GrossRevenue)
                self.find_and_update_item(soup, '營業利益（損失）', None,
                        Table.Items, Items.OperatingIncome)
                self.find_and_update_item(soup, '本期淨利（淨損）', None,
                        Table.Items, Items.NetIncome)
                self.find_and_update_item(soup, '　　利息收入', None,
                        Table.Items, Items.InterestIncome)
                self.find_and_update_item(soup, '營業成本合計', None,
                        Table.Items, Items.COST)
                self.find_and_update_item(soup, '稅前淨利（淨損）', None,
                        Table.Items, Items.NetIncomeBeforeTax)
                self.find_and_update_item(soup, '　營業外收入及支出合計', None,
                        Table.Items, Items.TotalNonOperatingRevenue)
                self.find_and_update_item(soup, '　營業費用合計', None,
                        Table.Items, Items.OperatingExpenses)
                self.find_and_update_item(soup, '　基本每股盈餘', None,
                        Table.Items, Items.EPS)
        except Exception as e:
            print("{0} at update_profit_and_lose".format(e))
            return False
        return True

    def update_cash_flow(self, year, season):
        key = "{0}.{1}".format(year, season)
        backup_folder = "./{0}/{1}".format(self.stock_id, key)
        os.makedirs(backup_folder, exist_ok = True)
        backup_file = "{0}/c.html".format(backup_folder)
        try:
            if not os.path.exists(backup_file):
                time.sleep(3);
                okay = self.crawl(backup_file, CashFlowStatement, year, season)
                if not okay:
                    return False
            if os.path.exists(backup_file):
                con = open(backup_file, mode="r", encoding="UTF-8").read()
                soup = bs4.BeautifulSoup(con, 'html.parser')
                self.find_and_update_item(soup, '營業活動之淨現金流入（流出）', None,
                        Table.Items, Items.CASHO)
                self.find_and_update_item(soup, '　投資活動之淨現金流入（流出）', None,
                        Table.Items, Items.CASHI)
                self.find_and_update_item(soup, '　處分不動產、廠房及設備', None,
                        Table.Items, Items.PFA)
                self.find_and_update_item(soup, '　取得不動產、廠房及設備', None,
                        Table.Items, Items.SFA)
                self.find_and_update_item(soup, '　籌資活動之淨現金流入（流出）', None,
                        Table.Items, Items.CAFA)
                self.find_and_update_item(soup, '　發放現金股利', None,
                        Table.Items, Items.CashDividends)
        except Exception as e:
            print("{0} at update_cash_flow".format(e))
            return False
        return True

    def find_and_update_item(self, soup, name, old_name, target, key):
        mylist = self.database[target].setdefault(key, [])
        table = soup.findAll(text=name)
        if not table and old_name:
            table = soup.findAll(text=old_name)
        if table:
            mylist.insert(0, float(table[0].parent.findNext('td').text.strip().replace(',', '')))
        else:
            mylist.insert(0, 0)

    def crawl(self, file, url, year, season):
        # encodeURIComponent=1&step=1&firstin=1&off=1&co_id=3056&year=109&season=3
        try:
            print("Try to crawl data for {}@{}.{}".format(self.stock_id, year, season))
            form_data = {
                    'encodeURIComponent': 1,
                    'step': 1,
                    'firstin': 1,
                    'off': 1,
                    'co_id': self.stock_id,
                    'year': year,
                    'season': season,
                    }

            resp = requests.post(url, form_data)
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')
            table = soup.findAll(text='查無所需資料！')
            if not table:
                table = soup.findAll(text='上市、上櫃及興櫃公司101年(含)以前之財報資料請至採IFRSs前之')
            if not table:
                table = soup.findAll(text='Overrun - 查詢過於頻繁,請稍後再試!!')
            if not table:
                with open(file, 'wb') as fd:
                    for chunk in resp.iter_content(chunk_size=1024):
                        fd.write(chunk)
                return True
        except Exception as e:
            return False
        return False

    def which_season(self):
        # get the current day of the year
        doy = datetime.date.today().timetuple().tm_yday
        # "day of year" ranges for the northern hemisphere
        one = range(0, 90)
        two = range(91, 180)
        three = range(181, 240)
        # winter = everything else

        if doy in one:
            season = 1
        elif doy in two:
            season = 2
        elif doy in three:
            season = 3
        else:
            season = 4
        return season

    def which_year(self):
        year = datetime.datetime.now().year
        return year-1911

# STEP 1
# Install Mandarin TTF into mpl-data/fonts/ttf/
# import matplotlib
# print(matplotlib.__file__)
# STEP 2
# go to ~/.matplotlib/ to remove cache
plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
#candidates = (5904, 2912, 5903, 2345, 2330, 3034, 1216, 1215, 2377, 2379, 1101, 1102, 0)
candidates = (5904, 0)
table = prettytable.PrettyTable(Titles)
for i, id in enumerate(candidates, start=1):
    if id != 0:
        s = StockHelper(i, id)
        s.crawl_year_report()
        s.calcuate_and_save()
        s.dump_table(table)
text = table.get_html_string()
text = html.unescape(text)
print(text)
