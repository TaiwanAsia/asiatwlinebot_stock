from base64 import encode
from random import random
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import random, re, time, _thread
from datetime import datetime, timedelta, timezone
import json, requests, urllib.request, chardet, sys
import logging
from crawler import crawler
from models.shared_db_model import db
from models.stock_model import Stock


app = Flask(__name__)


# 匯入設定
import config
line_bot_api = LineBotApi(config.line_bot_api)
handler = WebhookHandler(config.handler)
app.config['SQLALCHEMY_DATABASE_URI'] = config.app_config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    ##########  1 使用者輸入關鍵字查詢
    message = str(message).strip()

    # 正規表達過濾出純數字
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')

    company_uni_id = ''
    stock_code   = ''
    company_name   = ''

    ##########  1-1 關鍵字為INT
    if pattern.match(message):
        
        if len(message) == 8:
            ##########  1-1-1 使用者輸入統一編號
            print(f"\n ------------ 統一編號查詢公司  {message} ------------")

            url      = requests.get("https://company.g0v.ronny.tw/api/show/{0}".format(message))
            text     = url.text
            json_obj = json.loads(text)

            if '名稱' in json_obj['data']:
                company_uni_id = message
                company_name   = json_obj['data']['名稱']

            elif '公司名稱' in json_obj['data']:
                company_uni_id = message
                company_name = json_obj['data']['公司名稱']

            if company_name:
                # 公司名稱 找出 股票代號
                result = get_stockCode_by_companyName(company_name)
                if result:
                    company_name, stock_code = result
                search_output(reply_token, company_uni_id, company_name, stock_code, user_id)

            else:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))

        elif len(message) == 4:
            ##########  1-1-2 使用者輸入股票代號
            print(f"\n ------------ 股票代號查詢公司  {message} ------------")

            # 確認公司股票代號是否存在
            result = check_stockCode(message)
            if result:
                company_name, stock_code = result

                # 公司名稱 找出 公司統一編號
                result = get_companyUniId_by_companyName(company_name)
                if result:
                    company_uni_id, company_name = result
                    search_output(reply_token, company_uni_id, company_name, stock_code, user_id)

                else:
                    # 有股票代號，一定有統一編號
                    pass

            else:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))
        
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料。"))


    ########## 1-2 關鍵字非INT
    else:
        ########## 1-2-1 使用者輸入公司名稱
        company_name = message
        stock_code = False

        print(f"\n ------------ 依公司名稱查詢公司 Company_name: {company_name} ------------")

        print(str(datetime.now()))

        # 如輸入簡稱，則直接替換公司全名 company_name
        sql = f"SELECT * FROM stock where stock_name = '{company_name}'"
        company = db.engine.execute(sql).fetchone()

        print(str(datetime.now()))

        if company is not None:
            stock_code   = company[1]
            company_name = company[3]
            company_uni_id = get_companyUniId_by_companyName(company_name)[0]
            search_output(reply_token, company_uni_id, company_name, stock_code, user_id)
            return

        url = requests.get("https://company.g0v.ronny.tw/api/search?q={0}".format(company_name))
        text = url.text
        json_obj = json.loads(text)
        json_obj_len = json_obj['found']

        if json_obj_len < 1:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料耶..."))
        
        elif json_obj_len == 1:
            candidate = json_obj['data'][0]
            company_uni_id = candidate['統一編號']

            if '名稱' in candidate and candidate['名稱'] == company_name:
                company_name = candidate['名稱']
            if '公司名稱' in candidate and candidate['公司名稱'] == company_name:
                company_name = candidate['公司名稱']

            if company_name:
                if stock_code is False:
                    # 公司名稱 找出 股票代號
                    result = get_stockCode_by_companyName(company_name)
                    if result:
                        company_name, stock_code = result
                search_output(reply_token, company_uni_id, company_name, stock_code, user_id)
            else:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料耶..."))
            
        else:
            candidates = []
            for candidate in json_obj['data']:
                if '名稱' in candidate:
                    candidates.append([candidate['名稱'], candidate['統一編號']])
                if '公司名稱' in candidate:
                    candidates.append([candidate['公司名稱'], candidate['統一編號']])
                if '商業名稱' in candidate:
                    candidates.append([candidate['商業名稱'], candidate['統一編號']])

            # 載入Flex template
            FlexMessage = json.load(open('templates/template.json','r',encoding='utf-8'))
            FlexMessage['contents'][0]['header']['contents'][0]['text'] = company_name
            candidates_list = []
            
            for candidate in candidates:
                company_uni_id = candidate[1]
                company_name   = candidate[0]
                if company_name:
                    # 公司名稱 找出 股票代號
                    result = get_stockCode_by_companyName(company_name)
                    if result:
                        company_name, stock_code = result
                cand =  {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": f"{company_name}",
                        "data": f"company_search&{company_uni_id}&{company_name}&{stock_code}"
                    }
                }
                candidates_list.append(cand)

            if json_obj_len > 10:
                cand =  {
                    "type": "text",
                    "text": f"共有{json_obj_len}筆，建議搜尋精準關鍵字",
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



@handler.add(PostbackEvent)
def handle_postback(event):
    ts = str(event.postback.data)
    # print("Postback: " + ts)
    action = ts.split("&")[0]
    # keyword = str(ts.split("&")[1])
    user_id = event.source.user_id
    reply_token = event.reply_token
    nowdate = datetime.now().strftime("%Y-%m-%d")
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ########## 2-1 回傳公司資料
    if action == "company_search":
        company_uni_id = int(ts.split("&")[1])
        company_name   = str(ts.split("&")[2])
        stock_code     = str(ts.split("&")[3])

        # 輸出公司查詢結果
        search_output(reply_token, company_uni_id, company_name, stock_code, user_id)

    ########## 2-2 我想買賣
    if action == "tradeInfo":
        company_name     = str(ts.split("&")[1])
        company_uni_id   = int(ts.split("&")[2])

        sql = 'SELECT * FROM dataset_day where `company_name` like "%%{0}%%"'.format(company_name[:4])
        companies = db.engine.execute(sql).fetchall()

        # 未上市熱門股
        if len(companies) > 1:
        
            FlexMessage = json.load(open('templates/tradeInfo_stock.json','r',encoding='utf-8'))
            BoxTop = FlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = company_name

            Target_buy  = FlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][0]
            Target_sell = FlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][1]
            
            sql = 'SELECT buy_amount FROM dataset_day where `website_id` = 1 and `company_name` like "%%{0}%%"'.format(company_name[:4])
            max_buy_amount = db.engine.execute(sql).fetchone()[0]
            Target_buy['contents'][0]['text'] = max_buy_amount
            Target_buy['contents'][2]['text'] = companies[0]['buy_average']

            sql = 'SELECT sell_amount FROM dataset_day where `website_id` = 1 and `company_name` like "%%{0}%%"'.format(company_name[:4])
            max_sell_amount = db.engine.execute(sql).fetchone()[0]
            Target_sell['contents'][0]['text'] = max_sell_amount
            Target_sell['contents'][2]['text'] = companies[0]['sell_average']

            # WantBox = FlexMessage['body']['contents'][1]['contents'][1]['contents']

            WantBox_buy  = FlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
            WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&1&{company_name[:4]}" 
            WantBox_sell = FlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
            WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&2&{company_name[:4]}"

            
        else:
            FlexMessage = json.load(open('templates/tradeInfo.json','r',encoding='utf-8'))
            BoxTop = FlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = company_name
            BoxMid = FlexMessage['body']['contents'][1]['contents'][1]['contents'][3]
        
    

        line_bot_api.reply_message(reply_token, FlexSendMessage('tradeInfo',FlexMessage))

    ########## 3-1 我想買、我想賣
    if action == 'iwanttrade':
        user         = str(ts.split("&")[1])
        act          = str(ts.split("&")[2])
        company_name = ts.split("&")[3]
        company_type = ts.split("&")[4]
        print("\n\n")
        print(user + ' ' + act + ' ' + company_name + company_type)



######### 以下放多次使用的 def #########

# 輸出公司查詢結果 : 基本資料
def search_output(reply_token, company_uni_id, company_name, stock_code, user_id):
    print(f"\n ------------ 輸出公司查詢結果  {company_uni_id} {company_name} {stock_code}------------")

    FlexMessage = json.load(open('templates/company_info.json','r',encoding='utf-8'))
    FlexMessage['body']['contents'][0]['text'] = f"{company_name}"
    FlexMessage['body']['contents'][1]['text'] += f"     {company_uni_id}"
    FlexMessage['body']['contents'][2]['text'] += f"     {stock_code}"
    elements = FlexMessage['body']['contents'][3]['contents']
    for element in elements:
        ele_type     = element['type']
        if ele_type == 'button':
            action_type  = element['action']['type']
            action_label = element['action']['label']
            if action_type == 'uri':
                if action_label == '公司基本資料':
                    element['action']['uri'] = str(element['action']['uri']) + f"{company_uni_id}"
                elif action_label == '公司關係圖':
                    element['action']['uri'] = str(element['action']['uri']) + f"{company_uni_id}" + "&openExternalBrowser=1"
                elif action_label == '股權異動查詢':
                    pass
                else:
                    element['action']['uri'] = str(element['action']['uri']) + f"{stock_code}"
            if action_type == 'postback':
                element['action']['data'] = str(element['action']['data']) + f"{company_name}&{company_uni_id}"

    CarouselMessage = {
        "type": "carousel",
        "contents": []
    }
    CarouselMessage['contents'].append(FlexMessage)
    StockInfo = search_output_stockInfo(company_name, user_id)
    CarouselMessage['contents'].append(StockInfo)

    line_bot_api.reply_message(reply_token, FlexSendMessage('Company Info',CarouselMessage))



# 輸出公司查詢結果 : 股市資料
def search_output_stockInfo(company_name, user_id):
    print(f"\n ------------ 輸出公司股市資料  {company_name}------------")

    FlexMessage = json.load(open('templates/tradeInfo_stock.json','r',encoding='utf-8'))

    sql = 'SELECT * FROM `stock` where `stock_full_name` = "{0}"'.format(company_name)
    company = db.engine.execute(sql).fetchone()

    # 上市
    if company is not None:
        company_type = 1
        BoxTop = FlexMessage['body']['contents'][0]
        BoxTop['contents'][0]['text'] = company_name
        WantBox_sell  = FlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        WantBox_buy = FlexMessage['body']['contents'][1]['contents'][1]['contents'][2]

        WantBox_sell  = FlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{company_name[:4]}&{company_type}"
        WantBox_buy = FlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{company_name[:4]}&{company_type}"
    
    # 未上市
    else:
        company_type = 2
        sql = 'SELECT * FROM dataset_day where `company_name` like "%%{0}%%"'.format(company_name[:4])
        companies = db.engine.execute(sql).fetchall()
        # 尚未遇到未上市名稱前4字相同問題，目前只取第一筆。

        if len(companies) > 1:
            BoxTop = FlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = company_name

            Target_buy  = FlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][0]
            Target_sell = FlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][1]
            
            sql = 'SELECT buy_amount FROM dataset_day where `website_id` = 1 and `company_name` like "%%{0}%%"'.format(company_name[:4])
            max_buy_amount = db.engine.execute(sql).fetchone()[0]
            Target_buy['contents'][0]['text'] = max_buy_amount
            Target_buy['contents'][2]['text'] = companies[0]['buy_average']

            sql = 'SELECT sell_amount FROM dataset_day where `website_id` = 1 and `company_name` like "%%{0}%%"'.format(company_name[:4])
            max_sell_amount = db.engine.execute(sql).fetchone()[0]
            Target_sell['contents'][0]['text'] = max_sell_amount
            Target_sell['contents'][2]['text'] = companies[0]['sell_average']

            WantBox_sell  = FlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
            WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{company_name[:4]}&{company_type}"
            WantBox_buy = FlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
            WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{company_name[:4]}&{company_type}"
            
        else:
            FlexMessage = json.load(open('templates/tradeInfo.json','r',encoding='utf-8'))
            BoxTop = FlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = company_name
            BoxTop['contents'][1]['text'] = "未發行股票"
            FlexMessage['body']['contents'].pop(1)

    return FlexMessage


# 用 公司名稱 找出 公司統一編號
def get_companyUniId_by_companyName(company_name):
    if not company_name:
        return False
    
    url  = requests.get("https://company.g0v.ronny.tw/api/search?q={0}".format(company_name))
    text = url.text
    json_obj = json.loads(text)

    if not json_obj['data']:
        return False

    # 如有公司名稱部分重複，精準找出目標公司
    for candidate in json_obj['data']:
        company_uni_id = candidate['統一編號']

        if '名稱' in candidate and candidate['名稱'] == company_name:
            company_name = candidate['名稱']
        if '公司名稱' in candidate and candidate['公司名稱'] == company_name:
            company_name = candidate['公司名稱']
    return [company_uni_id, company_name]



# 用 公司名稱 找出 股票代號
def get_stockCode_by_companyName(company_name):
    if company_name:
        sql = 'SELECT * FROM stock where `stock_full_name` = "{0}"'.format(company_name)
        company = db.engine.execute(sql).fetchone()
        if company is not None:
            return [company[3], company[1]]
    return False

        
        

# 確認公司股票代號是否存在
def check_stockCode(stock_code):
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C".format(stock_code)
    html  = requests.get(url)
    
    html_text = html.text
    json_obj = json.loads(html_text)

    if not json_obj['msgArray']:
        return False
    
    company_name = json_obj['msgArray'][0]['nf']
    stock_code = stock_code
    return [company_name, stock_code]
    
        
    


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
    