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



class Dataset_day(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, nullable=False)
    table_name = db.Column(db.Text, nullable=False)
    order      = db.Column(db.Integer, nullable=True)
    company_name = db.Column(db.Text, nullable=True)
    buy_amount = db.Column(db.Text, nullable=True)
    buy_high = db.Column(db.Text, nullable=True)
    buy_low = db.Column(db.Text, nullable=True)
    buy_average = db.Column(db.Text, nullable=True)
    buy_average_yesterday = db.Column(db.Text, nullable=True)
    buy_change_percent = db.Column(db.Text, nullable=True)
    sell_amount = db.Column(db.Text, nullable=True)
    sell_high = db.Column(db.Text, nullable=True)
    sell_low = db.Column(db.Text, nullable=True)
    sell_average = db.Column(db.Text, nullable=True)
    sell_average_yesterday = db.Column(db.Text, nullable=True)
    sell_change_percent = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    def __repr__(self):
        return '<Dataset_day %r>' % self.dataset_day

class Website(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.Text, nullable=False)
    domain = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)
    def __repr__(self):
        return '<Website %r>' % self.website

# class Company_l_o(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     userid = db.Column(db.String(80), nullable=False)
#     date = db.Column(db.DateTime, nullable=False)
#     activity = db.Column(db.Text, nullable=False)
#     status = db.Column(db.String(80), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
#     def __repr__(self):
#         return '<Company_l_o %r>' % self.company_l_o



db.init_app(app)



#################################  爬蟲
def crawler():
    while 1 == 1:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        now = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區

        if now.hour == 14 and now.minute == 12:

            # Clear data
            sql = "TRUNCATE `linebot_stock`.`dataset_day`;"
            db.engine.execute(sql)

            ######  必富網熱門Top100 website_id=1  ######
            print(f"\n ------------ 爬蟲開始: 必富網熱門Top100 ------------")
            website_id = 1
            fp = urllib.request.urlopen('https://www.berich.com.tw/DP/OrderList/List_Hot.asp').read()
            text = fp.decode('Big5')
            soup = BeautifulSoup(text, features='lxml')

            # Find data
            target_table = soup.select_one('.sin_title').find_parent('table')
            target_trs = target_table.find_all('tr')
        
            # Set data
            dataset = []
            for tr in target_trs:
                td = tr.find_all('td')
                row = [i.text for i in td]
                dataset.append(row)

            # 整理欄位
            dataset[0][0]  = 'order'
            dataset[0][6]  = '買昨均'
            dataset[0][7]  = '買漲跌幅'
            dataset[0][12] = '賣昨均'
            dataset[0][13] = '賣漲跌幅'

            dataset_list = []
            for data in dataset:
                if data[0] and data[0] != 'order':
                    dataset_list.append(dict(zip(dataset[0], data)))

            # Insert data
            for dataset in dataset_list:
                newInput = Dataset_day(website_id=website_id, table_name='hotTop100', order=dataset['order'],
                company_name=dataset['未上市櫃股票公司名稱'], buy_amount=dataset['★買張'], buy_high=dataset['買高'], buy_low=dataset['買低']
                , buy_average=dataset['買均'], buy_average_yesterday=dataset['買昨均'], buy_change_percent=dataset['買漲跌幅'], sell_amount=dataset['★賣張']
                , sell_high=dataset['賣高'], sell_low=dataset['賣低'], sell_average=dataset['賣均'],
                sell_average_yesterday=dataset['賣昨均'], sell_change_percent=dataset['賣漲跌幅'])
                db.session.add(newInput)
                db.session.commit()

            print(f"\n ------------ 爬蟲結束: 必富網熱門Top100 ------------")
            ######  必富網結束  ######



            ######  台灣投資達人熱門Top100 website_id=2  ######
            print(f"\n ------------ 爬蟲開始: 台灣投資達人熱門Top100 ------------")
            website_id = 2
            body = urllib.request.urlopen('http://www.money568.com.tw/Order_Hot.asp').read()
            soup = BeautifulSoup(body, features='lxml')

            # Locate data
            target_table = soup.select_one("table.order_table_dv")
            target_trs = target_table.find_all('tr')

            # Set data
            dataset = []
            for idx, tr in enumerate(target_trs):
                if idx > 0 and idx <= 100:
                    td = tr.find_all('td')
                    row = [i.text for i in td]
                    dataset.append(row)
            
            # Insert data
            for data in dataset:
                newInput = Dataset_day(website_id=website_id, table_name='hotTop100', company_name=data[1],
                    buy_amount=data[5], buy_average=data[2], buy_average_yesterday=data[3], buy_change_percent=data[4],
                    sell_amount=data[9], sell_average=data[6], sell_average_yesterday=data[7], sell_change_percent=data[8])
                db.session.add(newInput)
                db.session.commit()
            
            print(f"\n ------------ 爬蟲結束: 台灣投資達人熱門Top100 ------------")
            ######  台灣投資達人結束  ######


        time.sleep(58)
    

# 監測
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # print('body'+body)
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

    message == str(message)

    # 正規表達過濾出純數字
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    number = pattern.match(message)

    # keyword 是數字
    if number:
        print(f"\n ------------ 統編or股票代號查詢公司  {message} ------------")

        company_uni_id = ''
        company_code   = ''
        company_name   = ''

        # 先判斷統一編號
        url      = requests.get("https://company.g0v.ronny.tw/api/show/{0}".format(message))
        text     = url.text
        json_obj = json.loads(text)

        if '名稱' in json_obj['data']:
            company_uni_id = message
            company_name   = json_obj['data']['名稱']

        elif '公司名稱' in json_obj['data']:
            company_uni_id = message
            company_name = json_obj['data']['公司名稱']


        # 再判斷股票代號
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


    # keyword 非數字
    else:
        # 公司名稱搜尋
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
            FlexMessage = json.load(open('template.json','r',encoding='utf-8'))
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
    today = datetime.now().strftime("%Y-%m-%d")
    todaytime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    if action == "company_search":
        company_name = str(ts.split("&")[1])
        company_id   = int(ts.split("&")[2])

        # 輸出公司查詢結果
        search_output(reply_token, company_id, company_name)


    if action == "tradeInfo":
        company_name = str(ts.split("&")[1])
        company_id   = int(ts.split("&")[2])

        sql = 'SELECT * FROM dataset_day where `company_name` like "%%{0}%%"'.format(company_name[:4])
        companies = db.engine.execute(sql).fetchall()

        # 未上市熱門股
        if len(companies) > 1:
        
            FlexMessage = json.load(open('tradeInfo_stock.json','r',encoding='utf-8'))
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
            FlexMessage = json.load(open('tradeInfo.json','r',encoding='utf-8'))
            BoxTop = FlexMessage['body']['contents'][0]
            BoxTop['contents'][0]['text'] = company_name
            BoxMid = FlexMessage['body']['contents'][1]['contents'][1]['contents'][3]
        
    

        line_bot_api.reply_message(reply_token, FlexSendMessage('tradeInfo',FlexMessage))

    
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

    FlexMessage = json.load(open('company_info.json','r',encoding='utf-8'))
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


# Message event: Sticker
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("--------------------STICKER--------------------")
    reply_token = event.reply_token
    sticker = random.randint(1988, 2027);
    line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=446, sticker_id=sticker))


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', config.port))
    _thread.start_new_thread(crawler, ())
    app.run(host='0.0.0.0', port=port)