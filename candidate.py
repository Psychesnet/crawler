# -*- coding: utf-8 -*-
from functions import parse_and_save

candidate = [\
        ['1216', '統一'], \
        ['2884', '玉山金'], \
        ['1717', '長興材料'], \
        ['2002', '中鋼'], \
        ['1232', '大統益'], \
        ['1301', '台朔'], \
        ['1303', '南亞'], \
        ['2201', '裕隆'], \
        ['2353', '宏碁'], \
        ['9921', '巨大'], \
        ['2351', '順德'], \
        ['9930', '中聯資'], \
        ['5871', '中租-KY'], \
        ['9941', '裕融'], \
        ['6592', '和潤'], \
        ['9904', '寶成'], \
        ['2204', '中華車'], \
        ['2330','台積電']\
        ]

parse_and_save(candidate, "candidate")

tradition = [\
        ["1210", "大成"], \
        ["1232", "大統益"], \
        ["2412", "中華電"], \
        ["3045", "台灣大哥大"], \
        ["9917", "中興保"], \
        ["9925", "新光保"], \
        ["2884", "玉山金"], \
        ["2880", "華南金"], \
        ["2887", "台新金"], \
        ["5580", "合庫金"], \
        ["2820", "華票"], \
        ["2882", "國泰金"], \
        ["2891", "中信金"], \
        ["2883", "中華開發"], \
        ["2834", "台企銀"], \
        ["2892", "台一金"], \
        ["2881", "富邦金"], \
        ["2886", "兆豐金"], \
        ["2889", "國票金"], \
        ["2801", "彰銀"], \
        ["9908", "大台北"], \
        ["9918", "欣天然"], \
        ["8926", "台汽電"], \
        ["1723", "中碳"], \
        ["2002", "中鋼"], \
        ["1326", "台化"], \
        ["9930", "中聯資"], \
        ["1101", "台泥"], \
        ["1102", "亞泥"], \
        ["1712", "興農"], \
        ["1537", "廣隆"], \
        ["2616", "山隆"], \
        ["6729", "胡連"], \
        ["1817", "凱撒衛"], \
        ["1722", "台肥"], \
        ["5604", "中連貨"], \
        ["1229", "聯華"], \
        ["5903", "全家"], \
        ["1216", "統一"] \
        ]

parse_and_save(tradition, "tradition")
