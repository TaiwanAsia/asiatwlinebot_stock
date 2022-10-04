from ast import If
from base64 import encode
from itertools import count
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
import json, requests, urllib.request, chardet
from bs4 import BeautifulSoup
import logging
from crawler import crawler
from models.shared_db import db
from models.dataset_day import Dataset_day


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

    #### 1 使用者輸入關鍵字查詢
    message == str(message)

    # 正規表達過濾出純數字
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    number = pattern.match(message)

    #### 1-1 關鍵字為INT
    if number:
        print(f"\n ------------ 統編or股票代號查詢公司  {message} ------------")

        company_uni_id = ''
        company_code   = ''
        company_name   = ''

        #### 1-1-1 使用者輸入統一編號
        url      = requests.get("https://company.g0v.ronny.tw/api/show/{0}".format(message))
        text     = url.text
        json_obj = json.loads(text)

        if '名稱' in json_obj['data']:
            company_uni_id = message
            company_name   = json_obj['data']['名稱']

        elif '公司名稱' in json_obj['data']:
            company_uni_id = message
            company_name = json_obj['data']['公司名稱']


        #### 1-1-2 使用者輸入股票代號
        url  = requests.get("https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C".format(message))
        text = url.text
        json_obj = json.loads(text)

        if json_obj['msgArray']:
            company_name = json_obj['msgArray'][0]['nf']
            company_code = message
        
        if company_name:
            url  = requests.get("https://company.g0v.ronny.tw/api/search?q={0}".format(company_name))
            text = url.text
            json_obj = json.loads(text)
            company_uni_id = json_obj['data'][0]['統一編號']

        
        search_output(reply_token, company_uni_id, company_name, company_code)


    #### 1-2 關鍵字非INT
    else:
        #### 1-2-1 使用者輸入公司名稱
        company_name = message

        print(f"\n ------------ 依公司名稱查詢公司 Company_name: {company_name} ------------")

        url = requests.get("https://company.g0v.ronny.tw/api/search?q={0}".format(company_name))
        text = url.text
        json_obj = json.loads(text)
        json_obj_len = json_obj['found']

        if json_obj_len < 1:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="是不是打錯了，找不到資料耶..."))
        
        elif json_obj_len == 1:
            company_uni_id = json_obj['data'][0]['統一編號']

            if '名稱' in json_obj['data'][0]:
                company_name = json_obj['data'][0]['名稱']
            if '公司名稱' in json_obj['data'][0]:
                company_name = json_obj['data'][0]['公司名稱']

            search_output(reply_token, company_uni_id, company_name)
            
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
                cand =  {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": f"{candidate[0]}",
                        "data": f"company_search&{candidate[0]}&{candidate[1]}"
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

    #### 2-1 回傳公司資料
    if action == "company_search":
        company_name = str(ts.split("&")[1])
        company_id   = int(ts.split("&")[2])

        # 輸出公司查詢結果
        search_output(reply_token, company_id, company_name)

    #### 2-2 我想買賣
    if action == "tradeInfo":
        company_name = str(ts.split("&")[1])
        company_id   = int(ts.split("&")[2])

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

    #### 3-1 我想買、我想賣
    if action == 'iwanttrade':
        user         = str(ts.split("&")[1])
        act          = str(ts.split("&")[2])
        company_name = ts.split("&")[3]
        print("\n\n")
        print(user + ' ' + act + ' ' + company_name)



######### 以下放多次使用的 def #########

# 輸出公司查詢結果
def search_output(reply_token, company_uni_id, company_name, company_code = ''):
    print(f"\n ------------ 輸出公司查詢結果  {company_uni_id} {company_name} {company_code}------------")

    FlexMessage = json.load(open('templates/company_info.json','r',encoding='utf-8'))
    FlexMessage['body']['contents'][0]['text'] = f"{company_uni_id} {company_name}"
    elements = FlexMessage['body']['contents'][1]['contents']
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
                    element['action']['uri'] = str(element['action']['uri']) + f"{company_code}"
            if action_type == 'postback':
                element['action']['data'] = str(element['action']['data']) + f"{company_name}&{company_uni_id}"

    line_bot_api.reply_message(reply_token, FlexSendMessage('Company Info',FlexMessage))




import os
if __name__ == "__main__":
    # 爬蟲執行時間
    target_time = [12, 2]

    port = int(os.environ.get('PORT', config.port))
    _thread.start_new_thread(crawler, (target_time[0], target_time[1], db))
    app.run(host='0.0.0.0', port=port, debug=False)