from ast import If
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
import json, requests, pathlib, pyimgur
# import plotly.graph_objects as go
# import networkx as nx
# from svglib.svglib import svg2rlg
# from reportlab.graphics import renderPM
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.common.exceptions import TimeoutException
# import unicodedata


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


# class Activities(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     userid = db.Column(db.String(80), nullable=False)
#     date = db.Column(db.DateTime, nullable=False)
#     activity = db.Column(db.Text, nullable=False)
#     status = db.Column(db.String(80), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
#     def __repr__(self):
#         return '<Activities %r>' % self.activity

# class Notes(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     userid = db.Column(db.String(80), nullable=False)
#     title = db.Column(db.Text, nullable=False)
#     status = db.Column(db.String(80), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
#     def __repr__(self):
#         return '<Notes %r>' % self.note

# class Activities_routine(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     userid = db.Column(db.String(80), nullable=False)
#     title = db.Column(db.Text, nullable=True)
#     frequency = db.Column(db.Text, nullable=False)
#     frequency_2 = db.Column(db.Text, nullable=True)
#     time = db.Column(db.Time, nullable=False)
#     end_date = db.Column(db.Date, nullable=True)
#     status = db.Column(db.String(80), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
#     def __repr__(self):
#         return '<Activities_routine %r>' % self.activity_routine



# db.init_app(app)



# ============開機推播============
# with app.app_context():
    # sql = "SELECT DISTINCT userid FROM activities"
    # Edata = db.engine.execute(sql).fetchall()
    # list2 = []
    # for event in Edata:
    #     list2.append(event[0])
    # reply = "金秘書跟您說早安！\n試著直接輸入行程名稱或點選下方選單開始使用～"
    # print(reply)
    # line_bot_api.multicast(list2, TextSendMessage(text=reply))
# ============開機推播============


    

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


    # [Step 0] or [統編查詢公司關係]

###################  以下嘗試將svg轉png後丟出  #######################

        # # The webpage is rendered dynamically with Javascript, so you will need selenium to get the rendered page.

        # url = "https://company-graph.g0v.ronny.tw/?id={0}".format("22099131")

        # #發送 GET 請求到 url，並將回應物件放到 resp
        # # resp = requests.get(url)

        # from selenium import webdriver
        # from selenium.webdriver.chrome.service import Service
        # from webdriver_manager.chrome import ChromeDriverManager
        # from selenium.webdriver.common.by import By

        # s=Service(ChromeDriverManager().install())

        # options = webdriver.ChromeOptions()
        # options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # options.add_experimental_option('useAutomationExtension', False)
        # options.add_experimental_option("prefs", {"profile.password_manager_enabled": False, "credentials_enable_service": False})

        # driver = webdriver.Chrome(service=s, options=options, service_log_path=os.devnull)
        # driver.maximize_window()
        # driver.get(url)
        # timeout = 10
        # try:
        #     element_present = EC.presence_of_element_located((By.ID, 'element_id'))
        #     WebDriverWait(driver, timeout).until(element_present)
        # except TimeoutException:
        #     print("Timed out waiting for page to load")

        # elements = driver.find_elements(By.XPATH, '//*[@id="parent"]')

        # parentElement = elements[0]

        # svg = parentElement.get_attribute('innerHTML')
        # # print(svg)
        # # print(type(svg))
        # # svg = svg.encode('utf-8')
        # # print(svg)
        # # print(type(svg))
        # # return

        # with open("temp/svgTest.svg", "w", encoding='utf-8') as svg_file:
        #     svg_file.write(svg)


        # url = requests.get("https://company-graph.g0v.ronny.tw/?id={0}".format("22099131"))
        # print(type(url))
        # print(url)
        # print("\n\n\n\n\n\n\n")

        # text = url.text
        # print(type(text))
        # print(text)
        
        # data = json.loads(text)
        # print(type(data))
        # print(data[0][0])

        # # 想辦法下載svg區塊

        # # 將下載的svg轉成png
        #     # 這裡要解決轉檔後中文變成亂碼: 編碼問題

        # drawing = svg2rlg('temp/svgTest.svg')
        # renderPM.drawToFile(drawing, 'temp/svgTest.png', fmt='PNG')

        # # 上傳png到imgur
        # CLIENT_ID = "b204114a90ad0e1"
        # im = pyimgur.Imgur(CLIENT_ID)
        # cur_path = pathlib.Path().resolve() / 'temp/'
        # dest_path = cur_path.__str__()+"/companysocialnetwork.png"
        # print(f"fileName: {dest_path}")
        # title = "Uploaded with PyImgur"
        # uploaded_image = im.upload_image(dest_path, title=title)
        # print(uploaded_image.title)
        # print(uploaded_image.link)
        # print(uploaded_image.type)
        

        # # 丟出imgur網址
        # image_message = ImageSendMessage(
        #     original_content_url=uploaded_image.link,
        #     preview_image_url=uploaded_image.link
        # )
        # line_bot_api.reply_message(reply_token, image_message)
###################  以上嘗試將svg轉png後丟出  #######################



    message == str(message)
    # 正規表達過濾出純數字
    pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
    result = pattern.match(message)

    if result:
        # company_id 可能是統一編號，也可能是股票代號
        company_id = message

        print(f"\n ------------ 依統編or股票代號查詢公司 Company_id: {company_id} ------------")

        FlexMessage = json.load(open('company_info.json','r',encoding='utf-8'))

        FlexMessage['body']['contents'][0]['text'] = FlexMessage['body']['contents'][0]['text'] + f": {company_id}"

        elements = FlexMessage['footer']['contents']
        for element in elements:
            if element['type'] == 'button' and element['action']['label'] != '股權異動查詢':
                element['action']['uri'] = str(element['action']['uri']) + f"{company_id}"
            if element['type'] == 'button' and element['action']['label'] == '公司關係圖(統編)':
                element['action']['uri'] = str(element['action']['uri']) + "&openExternalBrowser=1"



        line_bot_api.reply_message(reply_token, FlexSendMessage('Company Info',FlexMessage))






@handler.add(PostbackEvent)
# def handle_postback(event):
#     ts = str(event.postback.data)
#     # print("Postback: " + ts)
#     action = ts.split("&")[0]
#     # keyword = str(ts.split("&")[1])
#     user_id = event.source.user_id
#     reply_token = event.reply_token
#     today = datetime.now().strftime("%Y-%m-%d")
#     todaytime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#     # 新增固定行程 Step 1: 選擇頻率
#     if action == "add_routine_1":
#         print("\n ------------ 新增固定行程  Step 1: 選擇頻率 ------------")

#         keyword = str(ts.split("&")[1])
#         id      = int(ts.split("&")[2])

#         # 先刪 Step 0 新增的activity
#         sql = f"DELETE FROM `activities` WHERE (`id` = '{id}')"
#         db.engine.execute(sql)

#         # Step 1 選擇頻率
#         buttons_template_message = TemplateSendMessage(
#             alt_text='新增固定行程',
#             template=ButtonsTemplate(
#                 thumbnail_image_url='https://www.thirtyhandmadedays.com/wp-content/uploads/2020/07/printable-daily-schedule.jpg',
#                 image_aspect_ratio='rectangle',
#                 image_size='cover',
#                 image_background_color='#FFFFFF',
#                 title='固定行程 Step 1',
#                 text='選擇頻率',
#                 default_action=URIAction(
#                     label='view detail',
#                     uri='http://example.com/page/123'
#                 ),
#                 actions=[
#                     PostbackAction(
#                             label = "每日",
#                             display_text = "每日",
#                             data = f'add_routine_2&每日&{1}&{keyword}'
#                     ),
#                     PostbackAction(
#                             label = "每週",
#                             display_text = "每週",
#                             data = f'add_routine_2&每週&{1}&{keyword}'
#                     ),
#                     PostbackAction(
#                             label = "每月",
#                             display_text = "每月",
#                             data = f'add_routine_2&每月&{1}&{keyword}'
#                     ),
#                 ]
#             )
#         )
#         line_bot_api.reply_message(reply_token, buttons_template_message)




######### 以下放多次使用的 def #########



# 取得多個固定行程內容[Flex template]
# def get_V3_routines(activities_routine, reply_token, isPast):
#     if len(activities_routine) > 0:
#         contents = []
#         for routine in activities_routine:
#             contents.append({
#                 'type': 'button',
#                 'action': {
#                     'type' : 'postback',
#                     'label': f'{routine[2]}',
#                     'data' : f'routine&{routine[0]}'
#                 } 
#             })
#         Template = json.load(open('template.json','r',encoding='utf-8'))
#         Template['contents'][0]['body']['contents'] = contents
#         line_bot_api.reply_message(reply_token, FlexSendMessage('Template',Template))
#     else:
#         text = "查無此固定行程。"
#         line_bot_api.reply_message(reply_token, TextSendMessage(text = text))



# Message event: Sticker
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    print("--------------------STICKER--------------------")
    reply_token = event.reply_token
    sticker = random.randint(1988, 2027);
    line_bot_api.reply_message(event.reply_token,StickerSendMessage(package_id=446, sticker_id=sticker))


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8888))
    # _thread.start_new_thread(periodGuy, ())
    app.run(host='0.0.0.0', port=port)