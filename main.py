from base64 import encode
from random import random
from urllib.parse import quote
from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from crawler import crawler, parse_cnyesNews
from models.shared_db_model import db
from models.stock_model import Stock
from models.dataset_day_model import Dataset_day
from models.user_favorite_stock_model import User_favorite_stock
from models.stock_news_model import Stock_news
from find import get_company_by_name
from api import get_uniid_by_name, check_code_exist, get_company_by_uniid, find_by_name
from news import check_news
import re, time, _thread, copy, time
import json, requests, sys, pymysql


app = Flask(__name__)


# 匯入設定
import config
line_bot_api = LineBotApi(config.line_bot_api)
handler = WebhookHandler(config.handler)
app.config['SQLALCHEMY_DATABASE_URI'] = config.app_config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'connect_args': {
        'connect_timeout': 10
    },
    "pool_recycle": 1
}


db = SQLAlchemy(app)

db.init_app(app)


    

# 監測
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


# Message event: Text處理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text
    today = datetime.now().strftime("%Y-%m-%d")

    #####  1 使用者輸入關鍵字查詢
    message = str(message).strip()

    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$') # 正規表達過濾出純數字

    #####  1.1 關鍵字為INT
    if pattern.match(message):
        
        #####  1.1.1 使用者輸入統一編號
        if len(message) == 8:
            uniid = message
            company_name = get_company_by_uniid(uniid)
            if company_name is False:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))
                return
            company = Stock.find_by_fullname(company_name) # 搜尋Column: 公司全名
            if company is None:
                count, company = Stock.find_by_name(company_name) # 搜尋Column: 公司簡稱 (like搜尋)
            if company is None:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))
                return
            search_output(user_id, reply_token, uniid, company)

        #####  1.1.2 使用者輸入股票代號
        elif len(message) == 4:
            code = message
            company = Stock.find_by_code(code)
            if company is None:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))
                return
            if company.stock_full_name:
                name = company.stock_full_name
            else:
                name = company.stock_name
            uniid = get_uniid_by_name(name)[0]
            search_output(user_id, reply_token, uniid, company)
        
        ##### 1.1.3 找不到資料
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))


    ##### 1.2 關鍵字非INT
    else:
        ##### 1.2.1 使用者輸入公司名稱
        keyword = message

        count, company = Stock.find_by_fullname(keyword) # Step 1 : 搜尋公司全名
        print("\n", count, company)

        if company is None:
            # print("\n", 1)
            # print("\n", count, company)
            count, company = Stock.find_by_name(keyword) # Step 2 : 搜尋公司簡稱 (like搜尋)
        if count == 0:
            # print("\n", 2)
            # print("\n", count, company)
            count, company = Stock.find_by_fullname_like(keyword) # Step 3 : 搜尋公司全名 (like搜尋)

        if count == 0:
            # print("\n", 3)
            # print("\n", count, company)
            count, company = find_by_name(keyword) # Step 4 : 爬蟲後放進資料庫

        if count == 0:
            # print("\n", 4)
            # print("\n", count, company)
            line_bot_api.reply_message(reply_token, TextSendMessage(text="沒有資料。"))
            return

        if count > 1:
            # print("\n companies:   ", company)
            multiple_result_output(user_id, reply_token, keyword, company)
            return

        company = company[0]

        uniid = company.stock_uniid
        if uniid is None and company.stock_full_name:
            result = get_uniid_by_name(company.stock_full_name)
            if result:
                uniid = result[0]
                # print(uniid)
                sql = f"UPDATE stock SET stock_uniid = '{uniid}' WHERE id = '{company.id}'"
                db.engine.execute(sql)
                company = Stock.query.filter_by(id=company.id).first()

        search_output(user_id, reply_token, uniid, company)


@handler.add(PostbackEvent)
def handle_postback(event):
    ts = str(event.postback.data)
    action = ts.split("&")[0]
    user_id = event.source.user_id
    reply_token = event.reply_token
    nowdate = datetime.now().strftime("%Y-%m-%d")
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ##### 2.1 回傳公司資料
    if action == "company_search":
        id = int(ts.split("&")[1])
        stock = Stock.query.filter_by(id=id).first()
        uniid = stock.stock_uniid
        search_output(user_id, reply_token, uniid, stock) # 輸出查詢結果

    ##### 2.1 我想買、我想賣
    if action == 'iwanttrade':
        user         = str(ts.split("&")[1])
        act          = str(ts.split("&")[2])
        company_name = ts.split("&")[3]
        company_type = ts.split("&")[4]

    ##### 3.1 加入自選股
    if action == 'addFavorite':
        code = ts.split("&")[1]
        user_favorite_stock = User_favorite_stock.find_by_userid(user_id)
        codes = user_favorite_stock.stock_codes

        if user_favorite_stock is None:
            newInput = User_favorite_stock(user_userid=user_id, stock_codes='')
            db.session.add(newInput)
            db.session.commit()
            time.sleep(1)
            user_favorite_stock = User_favorite_stock.find_by_userid(user_id)

        if codes.find(code) < 0: # 未加入過此股
            if len(codes) > 0:
                codes += f',{code}'
            else: # 首次加入自選股
                codes += f'{code}'

        sql = f"UPDATE user_favorite_stock SET stock_codes = '{codes}' WHERE user_userid = '{user_id}'"
        db.engine.execute(sql)

        sql = f"SELECT * FROM user_favorite_stock WHERE user_userid = '{user_id}'"
        data = db.engine.execute(sql).fetchone()

        favorite_output(user_id, reply_token, data['stock_codes']) # 輸出




######### 以下放多次使用的 def #########


# 輸出公司查詢結果，分為
# 1.基本資料
# 2.股市資料
# 3.新聞
def search_output(user_id, reply_token, uniid, company):
    print(f"\n ------------ 輸出公司查詢結果  {company.stock_name}------------")

    if company is None:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))
        return

    stock_name = company.stock_name
    stock_code = company.stock_code
    stock_full_name = company.stock_full_name
    stock_type = company.stock_type

    CarouselMessage = {
        "type": "carousel",
        "contents": []
    }

    #
    # 1 基本資料
    FlexMessage = json.load(open('templates/company_info.json','r',encoding='utf-8'))

    FlexMessage['body']['contents'][0]['text'] = f"{stock_name}"
    FlexMessage['body']['contents'][1]['text'] += f"     {uniid}"
    FlexMessage['body']['contents'][2]['text'] += f"     {stock_code}"
    elements = FlexMessage['body']['contents'][3]['contents']
    for element in elements:
        ele_type     = element['type']
        if ele_type == 'button':
            action_type  = element['action']['type']
            action_label = element['action']['label']
            if action_type == 'uri':
                if action_label == '公司基本資料':
                    element['action']['uri'] = str(element['action']['uri']) + f"{uniid}"
                elif action_label == '公司關係圖':
                    element['action']['uri'] = str(element['action']['uri']) + f"{uniid}" + "&openExternalBrowser=1"
                elif action_label == '股權異動查詢':
                    pass
                else:
                    element['action']['uri'] = str(element['action']['uri']) + f"{stock_code}"
            if action_type == 'postback':
                element['action']['data'] = str(element['action']['data']) + f"{stock_name}&{uniid}"
    CarouselMessage['contents'].append(FlexMessage) # 放入Carousel


    #
    # 2 股市資料
    TradeinfoFlexMessage = json.load(open('templates/tradeInfo_stock.json','r',encoding='utf-8'))

    if stock_type == 1: # 未上市
        print("\n\n 股市資料 TradeinfoFlexMessage", stock_name)
        stock_data = Dataset_day.find_by_name(stock_name) # 目前取關鍵字前2個字去做模糊搜尋，結果有可能不只一筆 例: 前兩字為台灣，在此只取一筆 TODO: 1.回傳不同網站數字統計後結果。 2.多筆的話應 return emplates/template.json。

        if stock_data is None: # Dataset_day 沒資料的情況: 1.不在100熱門  2.沒這檔股票
            # print("\n\n", FlexMessage['body']['contents'], "\n\n")
            BoxTop = TradeinfoFlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = stock_name
            d = {
              "type": "text",
              "text": "無股票資料",
              "size": "xl",
              "weight": "bold",
              "align": "center"
            }
            BoxTop['contents'].append(d)
            TradeinfoFlexMessage['body']['contents'].pop(1)
            TradeinfoFlexMessage['body']['contents'].pop(-1)
        
        else:
            BoxTop = TradeinfoFlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = stock_name
            Target_buy  = TradeinfoFlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][0]
            Target_sell = TradeinfoFlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][1]
            Target_buy['contents'][0]['text'] = stock_data.buy_amount # 目前只使用必富網資料
            Target_buy['contents'][2]['text'] = stock_data.buy_average
            Target_sell['contents'][0]['text'] = stock_data.sell_amount # 目前只使用必富網資料
            Target_sell['contents'][2]['text'] = stock_data.sell_average
            WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
            WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{stock_name[:4]}&{stock_type}"
            WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
            WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{stock_name[:4]}&{stock_type}"
            TradeinfoFlexMessage["body"]["contents"][3]["action"]["data"] += f"&{stock_code}"

    # TODO: 爬上市股價
    elif stock_type == 2: # 上市
        BoxTop = TradeinfoFlexMessage['body']['contents'][0]
        BoxTop['contents'][0]['text'] = stock_full_name
        WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{stock_name[:4]}&{stock_type}"
        WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{stock_name[:4]}&{stock_type}"
        TradeinfoFlexMessage["body"]["contents"][3]["action"]["data"] += f"&{stock_code}"
        
    CarouselMessage['contents'].append(TradeinfoFlexMessage) # 放入Carousel

    #
    # 3 新聞
    NewsFlexMessage = json.load(open("templates/company_news.json","r",encoding="utf-8"))
    YearBoxSample = copy.deepcopy(NewsFlexMessage["body"]["contents"][1]) # 取出年份BOX當模板
    NewsBoxSample = copy.deepcopy(NewsFlexMessage["body"]["contents"][2]) # 取出新聞BOX當模板
    NewsFlexMessage["body"]["contents"] = NewsFlexMessage["body"]["contents"][:1] # 移除年份、新聞BOX，現在只剩公司名稱BOX
    
    check = Stock_news.today_update_check(stock_code)
    if check is None or len(check) < 1:
        line_bot_api.push_message(user_id,  TextSendMessage(text="替您蒐集新聞中，請稍後。"))

    StockNews = parse_cnyesNews(stock_name, stock_code)

    if StockNews is not None and len(StockNews[0].stock_news_title)>0:
        NewsFlexMessage["body"]["contents"][0]["text"] = stock_name # 修改公司名稱
        NewsByYear = {}
        ContentBox = [] # 年份&新聞BOX
        for news in StockNews:
            year = news.stock_news_date.split("-")[0]
            if year not in NewsByYear:
                NewsByYear[year] = []
            NewsByYear[year].append(news)
        for year in NewsByYear:
            YearBox = copy.deepcopy(YearBoxSample)
            YearBox["contents"][0]["text"] = year + "年"
            ContentBox.append(YearBox) # 先放年份
            for news in NewsByYear[year]:
                NewsBox = copy.deepcopy(NewsBoxSample)
                NewsBox["contents"][0]["contents"][0]["text"] = news.stock_news_title
                NewsBox["contents"][0]["contents"][0]["action"]['uri'] = news.stock_news_url
                NewsBox["contents"][0]["contents"][1]["text"] = news.stock_news_date.split("-")[1] + "/" + news.stock_news_date.split("-")[2]
                ContentBox.append(NewsBox) # 再放新聞
        NewsFlexMessage["body"]["contents"] += ContentBox # 把年份+新聞BOX加回去公司名稱BOX後
    else:
        NewsFlexMessage["body"]["contents"][0]["text"] = stock_name
        # NewsFlexMessage["body"]["contents"][1]["contents"][1]["contents"]["text"] = "無"
        # NewsFlexMessage["body"]["contents"][1]["contents"].pop()
    
    CarouselMessage["contents"].append(NewsFlexMessage) # 放入Carousel

    line_bot_api.reply_message(reply_token, FlexSendMessage('Company Info',CarouselMessage))



# 輸出使用者自選股
def favorite_output(userid, reply_token, codes):
    codes = codes.split(',')
    FavoriteFlexMessage = json.load(open("templates/user_stock.json","r",encoding="utf-8"))
    FavoriteFlexMessage["body"]["contents"].clear()
    for code in codes: # TODO 應該用 IN(code1, code2) 效率會比一直query好
        stock = Stock.find_by_code(code)
        box = {
                "type": "button",
                "action": {
                "type": "postback",
                "label": f"{stock.stock_name}　　500 / 股",
                "data": "stock"
                },
                "height": "sm"
        }
        FavoriteFlexMessage["body"]["contents"].append(box)
    line_bot_api.reply_message(reply_token, FlexSendMessage('Favorite Info', FavoriteFlexMessage))
        
    


#### TODO 
def multiple_result_output(user_id, reply_token, keyword, companies):

    # 載入Flex template
    FlexMessage = json.load(open('templates/template.json','r',encoding='utf-8'))
    FlexMessage['contents'][0]['header']['contents'][0]['text'] = keyword
    candidates_list = []

    for company in companies:
        if company.stock_uniid is None:
            result = get_uniid_by_name(company.stock_full_name)
            if result:
                uniid = result[0]
                sql = f"UPDATE stock SET stock_uniid = '{uniid}' WHERE id = '{company.id}'"
                db.engine.execute(sql)
                company = Stock.query.filter_by(id=company.id).first()
        if len(company.stock_full_name) > 0:
            name = company.stock_full_name
        else:
            name = company.stock_name
        cand =  {
            "type": "button",
            "action": {
                "type": "postback",
                "label": f"{name}",
                "data": f"company_search&{company.id}"
            }
        }
        candidates_list.append(cand)

    if len(companies) > 10:
        cand =  {
            "type": "text",
            "text": f"共有{len(companies)}筆，建議搜尋精準關鍵字",
            "color": "#aaaaaa",
            "size": "md",
            "weight": "bold",
            "style": "italic",
            "decoration": "underline",
            "align": "center"
        }
        candidates_list.append(cand)

    FlexMessage['contents'][0]['body']['contents'] = candidates_list

    line_bot_api.reply_message(reply_token, FlexSendMessage('Candidates Info',FlexMessage))






        
    


import os
if __name__ == "__main__":

    # Debug模式將無條件執行爬蟲
    debug = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '1' or sys.argv[1] == 'True':
            debug = True

    # 爬蟲執行時間
    target_time = [11, 37]
    
    _thread.start_new_thread(crawler, (target_time[0], target_time[1], db, debug, app))
    port = int(os.environ.get('PORT', config.port))
    app.run(host='0.0.0.0', port=port, debug=False)
    