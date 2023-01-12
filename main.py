from flask import Flask, request, abort, render_template
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.utils import secure_filename
from datetime import datetime
from crawler import crawler, parse_cnyesNews
from models.shared_db_model import db
from models.stock_model import Stock
from models import user_favorite_company_model, company_news_model, dataset_day_model, user_favorite_stock_model, company_model, industry_model
import api
# from api import get_uniid_by_name, get_company_by_uniid, parse_by_keyword
import re, _thread, copy
import json, sys,os
import pandas as pd
from common.logging import setup_logging
import logging


app = Flask(__name__)

UPLOAD_FOLDER = "./uploads/"
ALLOWED_EXTENSIONS = set(['csv'])

app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = 300 * 1024 * 1024  # 300MB

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


# db = SQLAlchemy(app)

db.init_app(app)


WeblogDir = 'web'
WebloggerName = WeblogDir+'allLogger'
setup_logging(WeblogDir)
Weblogger = logging.getLogger(WebloggerName)




@app.route("/home", defaults={'message':''}, methods=['GET', 'POST'])
def home(message):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            # filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'BGMOPEN1.csv'))
            result = bgmopen_operator()
            if result is False:
                return render_template("home.html", message='檔案上傳失敗')
            return render_template("home.html", message='成功!!')
        else:
            return render_template("home.html", message='檔案格式不符合')
    return render_template("home.html", message=message)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def bgmopen_operator():
    usecols = ['統一編號', '總機構統一編號', '營業人名稱', '資本額', '設立日期', '組織別名稱',
        '行業代號', '名稱', '行業代號1', '名稱1', '行業代號2', '名稱2', '行業代號3', '名稱3']
    data_type = {"統一編號": str, "總機構統一編號": str, '資本額': str, "設立日期": str, "行業代號": str
    , "行業代號1": str, "行業代號2": str, "行業代號3": str}
    pd_bgmopen = pd.read_csv("uploads/BGMOPEN1.csv", usecols=usecols, dtype=data_type)
    pd_bgmopen.columns = ['uniid', 'top_uniid', 'business_entity', 'capital', 'establishment_date', 'company_type',
        'industrial_classification', 'industrial_name', 'industrial_classification_1', 'industrial_name_1', 'industrial_classification_2', 'industrial_name_2',
        'industrial_classification_3', 'industrial_name_3']
    char_substitute = {
        b'\xf0\xa3\x87\x93' : '鼎',
        b'\xf0\xa7\x99\x97' : '佑',
        b'\xf0\xa5\xb4\x8a' : '𥴊'
    }
    for i in range(0,16):
        if i == 15:
            df = pd_bgmopen.iloc[100000*i : ]
        else:
            df = pd_bgmopen.iloc[1+100000*i : 100000*(1+i)]
        print(f'Data:  ',(1+100000*i) , '-', (100000*(1+i)))
        Weblogger.info(f'Data:  ',(1+100000*i) , '-', (100000*(1+i)))
        drop_indices = []
        for index, row in df.iterrows():
            if row['company_type'] in ['獨資', '合夥', '其他', '合作社']:
                drop_indices.append(index)
            for char_index, char in enumerate(row['business_entity']):
                if len(char.encode('utf-8')) > 3:
                    if char.encode('utf-8') in char_substitute:
                        replace = char_substitute[char.encode('utf-8')]
                    else:
                        replace = 'X'
                        # print(f'[{index}]-encode : ', row['uniid'], row['business_entity'], char.encode('utf-8'))
                    pd_bgmopen.loc[index, "business_entity"] = pd_bgmopen.iloc[index]['business_entity'][:char_index] + replace + pd_bgmopen.iloc[index]['business_entity'][char_index+1:]
        df.drop(drop_indices, axis=0, inplace=True)

        try:
            df.to_sql('company', db.engine, if_exists='append', index=False, chunksize=5000)
        except (exc.IntegrityError, exc.DataError) as e:
            Weblogger.error('Insert db.  數據錯誤')
            Weblogger.error(e)
            return False
        except Exception as e:
            Weblogger.error('Insert db.  未知錯誤')
            Weblogger.error(e)
            return False
        else:
            Weblogger.info(f'Insert db  Successfully.')
    return False

@app.route("/upstream_downstream", methods=['GET', 'POST'])
def upstream_downstream():
    
    if request.method == 'POST' and request.form.get('keyword') != '':
        keyword = request.form.get('keyword')
        sql = 'SELECT * FROM `industry` ORDER BY CONVERT(`name` using big5) ASC'.format("%%" + keyword + "%%")
        industries_all = db.engine.execute(sql).fetchall()
        sql = 'SELECT * FROM `industry` WHERE `name` LIKE "{0}" ORDER BY CONVERT(`name` using big5) ASC'.format("%%" + keyword + "%%")
        industries = db.engine.execute(sql).fetchall()
        updates = []
        for industry in industries:
            upstream_1   = request.form.get(f'{industry.id}_upstream_1')
            upstream_2   = request.form.get(f'{industry.id}_upstream_2')
            downstream_1 = request.form.get(f'{industry.id}_downstream_1')
            downstream_2 = request.form.get(f'{industry.id}_downstream_2')

            if upstream_1:
                updates.append(upstream_1)
            if upstream_2:
                updates.append(upstream_2)
            if downstream_1:
                updates.append(downstream_1)
            if downstream_2:
                updates.append(downstream_2)

        for row in updates:
            id, stream, stream_id = row.split("-")
            industry_model.Industry.update_stream(id, stream, stream_id)

        industries = db.engine.execute(sql).fetchall()
            
        return render_template("upstream_downstream.html", industries=industries, industries_all=industries_all, len=len(industries))
        
    return render_template("upstream_downstream.html")

@app.route("/get_industries", methods=['GET'])
def get_industries():
    industries = industry_model.Industry.query.limit(100).all()
    json_industries = json.dumps(industries)
    return json_industries
    

    


#############################################################
#                   上面區塊 web     程式碼                  #
#############################################################
#                   以下皆是 linebot 程式碼                  #
#############################################################




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
        
        #####  1.1.1 使用者輸入統一編號 - 使用Company
        if len(message) == 8:
            uniid = message
            company = company_model.Company.find_by_uniid(uniid)
            if company is None:
                line_bot_api.reply_message(reply_token, TextSendMessage(text="查無此公司，請再確認一次。"))
                return
            search_output(user_id, reply_token, company)

        #### 暫時不用
        #####  1.1.2 使用者輸入股票代號 - 使用Stock
        # elif len(message) == 4:
        #     code = message
        #     company = Stock.find_by_code(code)
        #     if company is None:
        #         line_bot_api.reply_message(reply_token, TextSendMessage(text="查無此公司，請再確認一次。"))
        #         return
        #     if company.stock_full_name:
        #         name = company.stock_full_name
        #     else:
        #         name = company.stock_name
        #     uniid = api.get_uniid_by_name(name)[0]
        #     search_output(user_id, reply_token, uniid, company)
        
        ##### 1.1.3 找不到資料
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="查無此公司，請再確認一次。"))


    ##### 1.2 關鍵字非INT
    else:
        ##### 1.2.1 使用者輸入公司名稱 - 使用Company
        keyword = message
        companies = company_model.Company.find_by_business_entity_like_search(keyword)
        if len(companies) == 0:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="查無此公司。"))
            return
        if len(companies) > 1:
            multiple_result_output_2(reply_token, keyword, companies)
            return

        search_output(user_id, reply_token, companies[0])


@handler.add(PostbackEvent)
def handle_postback(event):
    ts = str(event.postback.data)
    param = ts.split("&")
    action = param[0]
    user_id = event.source.user_id
    reply_token = event.reply_token
    nowdate = datetime.now().strftime("%Y-%m-%d")
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ##### 2.1 回傳公司資料
    # if action == "stock":
    #     id = int(ts.split("&")[1])
    #     stock = Stock.query.filter_by(id=id).first()
    #     search_output(user_id, reply_token, stock) # 輸出查詢結果

    if action == "company":
        company_id = int(ts.split("&")[1])
        company = company_model.Company.find_by_id(company_id)
        search_output(user_id, reply_token, company) # 輸出查詢結果

    ##### 2.1 我想買、我想賣
    if action == 'iwanttrade':
        user         = str(ts.split("&")[1])
        act          = str(ts.split("&")[2])
        company_name = ts.split("&")[3]

    ##### 3.1 加入自選股
    if action == 'addFavorite':
        company_id = param[1]
        favorite_company = user_favorite_company_model.User_favorite_company.find_by_userid(user_id)

        if favorite_company is None: # 首次新增自選股
            favorite_company = user_favorite_company_model.User_favorite_company(userid=user_id, company_ids='')
            db.session.add(favorite_company)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

        if favorite_company.company_ids.find(company_id) < 0: # 未加入過此股
            if len(favorite_company.company_ids) > 0:
                favorite_company.company_ids += f',{company_id}'
            else: # 首次新增自選股
                favorite_company.company_ids += f'{company_id}'

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(e)

        favorite_company = db.session.merge(favorite_company) # session 已经被提交(commit)，导致操作的 model 对象已经不在当前 session 中了。 解决的办法就是：把对象重新加入到当前 session 中
        favorite_output(reply_token, favorite_company.company_ids)

    ##### 3.2 移出自選股
    if action == 'delFavorite':
        company_id = param[1]
        favorite_company = user_favorite_company_model.User_favorite_company.find_by_userid(user_id)

        favorite_company_list = favorite_company.company_ids.split(",")
        favorite_company_list.remove(str(company_id))
        favorite_company.company_ids = ",".join(favorite_company_list)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
        
        favorite_company = db.session.merge(favorite_company) # session 已经被提交(commit)，导致操作的 model 对象已经不在当前 session 中了。 解决的办法就是：把对象重新加入到当前 session 中
        favorite_output(reply_token, favorite_company.company_ids)

    ##### 3.3 檢視自選股
    if action == 'viewFavorite':
        favorite_company = user_favorite_company_model.User_favorite_company.find_by_userid(user_id)
        if favorite_company is None:
            line_bot_api.reply_message(reply_token, TextSendMessage(text="您尚未加入自選股。"))
            return
        favorite_output(reply_token, favorite_company.company_ids)

    ##### 4.1 檢視產業鏈其他公司
    if action == 'industry_stream':
        code = param[1]
        if code == "-1":
            line_bot_api.reply_message(reply_token, TextSendMessage(text="此功能施工中..."))
            return
        
        industry = industry_model.Industry.get_by_code(code)
        results = company_model.Company.find_by_industry(code)
        output_companies = []
        # 優先找 1.未上市 2.有股價
        for result in results:
            stock_info = dataset_day_model.Dataset_day.find_by_company_name_like_search(result.business_entity)
            if stock_info is not None:
                output_companies.append(result)
        multiple_result_output_2(reply_token, industry.name, output_companies)
            


######### 以下放多次使用的 def #########


# 輸出公司查詢結果，分為
# 1.基本資料
# 2.股市資料
# 3.新聞
def search_output(user_id, reply_token, company):
    print(f"\n ------------ 輸出公司查詢結果 : {company.business_entity}------------")

    if company is None:
        line_bot_api.reply_message(reply_token, TextSendMessage(text="查無此公司，請再確認一次。"))
        return

    CarouselMessage = {
        "type": "carousel",
        "contents": []
    }

    #
    # 1 基本資料
    FlexMessage = json.load(open('templates/company_info.json','r',encoding='utf-8'))

    FlexMessage['body']['contents'][0]['text'] = f"{company.business_entity}"
    FlexMessage['body']['contents'][1]['text'] += f"     {company.uniid}"
    # FlexMessage['body']['contents'][2]['text'] += f"     {company_code}"
    elements = FlexMessage['body']['contents'][3]['contents']
    for element in elements:
        ele_type     = element['type']
        if ele_type == 'button':
            action_type  = element['action']['type']
            action_label = element['action']['label']
            if action_type == 'uri':
                if action_label == '公司基本資料':
                    element['action']['uri'] = str(element['action']['uri']) + f"{company.uniid}"
                elif action_label == '公司關係圖':
                    element['action']['uri'] = str(element['action']['uri']) + f"{company.uniid}" + "&openExternalBrowser=1"
                elif action_label == '股權異動查詢':
                    pass
                # else:
                #     element['action']['uri'] = str(element['action']['uri']) + f"{company_code}"
            if action_type == 'postback':
                element['action']['data'] = str(element['action']['data']) + f"{company.business_entity}&{company.uniid}"
    CarouselMessage['contents'].append(FlexMessage) # 放入Carousel


    added_already = False
    favorite_company = user_favorite_company_model.User_favorite_company.find_by_userid(user_id)
    if favorite_company is not None:
        if favorite_company.company_ids.find(str(company.id)) >= 0:
            added_already = True

    #
    # 2 股市資料
    TradeinfoFlexMessage = json.load(open('templates/tradeInfo_stock.json','r',encoding='utf-8'))

    company_stock_info = dataset_day_model.Dataset_day.find_by_company_name_like_search(company.business_entity) # 目前取關鍵字前2個字去做模糊搜尋，結果有可能不只一筆 例: 前兩字為台灣，在此只取一筆 TODO: 1.回傳不同網站數字統計後結果。 2.多筆的話應 return emplates/template.json。

    if company_stock_info is None: # Dataset_day 沒資料的情況: 1.不在100熱門  2.沒這檔股票
        # print("\n\n", FlexMessage['body']['contents'], "\n\n")
        BoxTop = TradeinfoFlexMessage['body']['contents'][0]
        BoxTop['contents'][0]['text'] = company.business_entity
        notFound = {
            "type": "text",
            "text": "無股票資料",
            "size": "xl",
            "weight": "bold",
            "align": "center"
        }
        BoxTop['contents'].append(notFound)
        TradeinfoFlexMessage['body']['contents'].pop(4)
        TradeinfoFlexMessage['body']['contents'].pop(3)
        TradeinfoFlexMessage['body']['contents'].pop(1)
    
    else:
        # if company_type == 1: # 未上市
        #     BoxTop = TradeinfoFlexMessage['body']['contents'][0]
        #     BoxTop['contents'][0]['text'] = company_name
        #     Target_buy  = TradeinfoFlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][0]
        #     Target_sell = TradeinfoFlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][1]
        #     Target_buy['contents'][0]['text'] = company_data.buy_amount # 目前只使用必富網資料
        #     Target_buy['contents'][2]['text'] = company_data.buy_average
        #     Target_sell['contents'][0]['text'] = company_data.sell_amount # 目前只使用必富網資料
        #     Target_sell['contents'][2]['text'] = company_data.sell_average
        #     WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        #     WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{company_name[:4]}&{company_type}"
        #     WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        #     WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{company_name[:4]}&{company_type}"
            

        # # TODO: 爬上市股價
        # elif company_type == 2: # 上市
        #     BoxTop = TradeinfoFlexMessage['body']['contents'][0]
        #     BoxTop['contents'][0]['text'] = company_full_name
        #     WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        #     WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        #     WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        #     WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{company_name[:4]}&{company_type}"
        #     WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        #     WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{company_name[:4]}&{company_type}"

        BoxTop = TradeinfoFlexMessage['body']['contents'][0]
        BoxTop['contents'][0]['text'] = company.business_entity
        Target_buy  = TradeinfoFlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][0]
        Target_sell = TradeinfoFlexMessage['body']['contents'][1]['contents'][0]['contents'][3]['contents'][1]
        Target_buy['contents'][0]['text'] = company_stock_info.buy_amount # 目前只使用必富網資料
        Target_buy['contents'][2]['text'] = company_stock_info.buy_average
        Target_sell['contents'][0]['text'] = company_stock_info.sell_amount # 目前只使用必富網資料
        Target_sell['contents'][2]['text'] = company_stock_info.sell_average
        WantBox_sell  = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][0]
        WantBox_sell['action']['data'] = WantBox_sell['action']['data'] + f"&{user_id}&sell&{company.business_entity[:4]}"
        WantBox_buy = TradeinfoFlexMessage['body']['contents'][1]['contents'][1]['contents'][2]
        WantBox_buy['action']['data'] = WantBox_buy['action']['data'] + f"&{user_id}&buy&{company.business_entity[:4]}"
        
        # TradeinfoFlexMessage["body"]["contents"][4]["action"]["data"] += f"&{id}" # 檢視自選股
    
        if added_already:
            TradeinfoFlexMessage["body"]["contents"][3]["action"]["label"] = "移出自選股"
            TradeinfoFlexMessage["body"]["contents"][3]["action"]["data"]  = f"delFavorite&{company.id}" # 取消自選股
        else:
            TradeinfoFlexMessage["body"]["contents"][3]["action"]["data"] += f"&{company.id}" # 加入自選股

    #
    # 產業鏈
    industry = industry_model.Industry.get_by_code(company.industrial_classification)
    TradeinfoFlexMessage['footer']['contents'][2]['contents'][0]['action']['data']  += f"&{industry.upstream_1 if industry.upstream_1 else -1}"
    TradeinfoFlexMessage['footer']['contents'][2]['contents'][1]['action']['label'] += f" - {industry.name}"
    TradeinfoFlexMessage['footer']['contents'][2]['contents'][1]['action']['data']  += f"&{industry.code}"
    TradeinfoFlexMessage['footer']['contents'][2]['contents'][2]['action']['data']  += f"&{industry.downstream_1 if industry.downstream_1 else -1}"

        
    CarouselMessage['contents'].append(TradeinfoFlexMessage) # 放入Carousel

    #
    # 3 新聞
    NewsFlexMessage = json.load(open("templates/company_news.json","r",encoding="utf-8"))
    YearBoxSample = copy.deepcopy(NewsFlexMessage["body"]["contents"][1]) # 取出年份BOX當模板
    NewsBoxSample = copy.deepcopy(NewsFlexMessage["body"]["contents"][2]) # 取出新聞BOX當模板
    NewsFlexMessage["body"]["contents"] = NewsFlexMessage["body"]["contents"][:1] # 移除年份、新聞BOX，現在只剩公司名稱BOX
    
    check = company_news_model.Company_news.today_update_check_by_company_id(company.id)
    if check is None or len(check) < 1:
        line_bot_api.push_message(user_id,  TextSendMessage(text="替您蒐集新聞中，請稍後。"))
        parse_cnyesNews(company.id, company.business_entity) # 爬蟲

    company_news = company_news_model.Company_news.today_update_check_by_company_id(company.id)

    if company_news is None or len(company_news) < 1:
        NewsFlexMessage["body"]["contents"][0]["text"] = "新聞"
    else:
        if len(company_news[0].news_title) > 0:
            NewsFlexMessage["body"]["contents"][0]["text"] = company_news[0].keyword + " - 新聞"
            NewsByYear = {}
            ContentBox = [] # 年份&新聞BOX
            for news in company_news:
                year = news.news_date.split("-")[0]
                if year not in NewsByYear:
                    NewsByYear[year] = []
                NewsByYear[year].append(news)
            for year in NewsByYear:
                YearBox = copy.deepcopy(YearBoxSample)
                YearBox["contents"][0]["text"] = year + "年"
                ContentBox.append(YearBox) # 先放年份
                for news in NewsByYear[year]:
                    NewsBox = copy.deepcopy(NewsBoxSample)
                    NewsBox["contents"][0]["contents"][0]["text"] = news.news_title
                    NewsBox["contents"][0]["contents"][0]["action"]['uri'] = news.news_url
                    NewsBox["contents"][0]["contents"][1]["text"] = news.news_date.split("-")[1] + "/" + news.news_date.split("-")[2]
                    ContentBox.append(NewsBox) # 再放新聞
            NewsFlexMessage["body"]["contents"] += ContentBox # 把年份+新聞BOX加回去公司名稱BOX後
        else:
            NewsFlexMessage["body"]["contents"][0]["text"] = company_news[0].keyword + " - 新聞"
    
    CarouselMessage["contents"].append(NewsFlexMessage) # 放入Carousel

    line_bot_api.reply_message(reply_token, FlexSendMessage('Company Info',CarouselMessage))



# 輸出使用者自選股
def favorite_output(reply_token, company_ids):
    FavoriteFlexMessage = json.load(open("templates/user_stock.json","r",encoding="utf-8"))
    # FavoriteFlexMessage["body"]["contents"].clear()

    companies = company_model.Company.find_by_ids(company_ids)

    for company in companies: # TODO 應該用 IN(code1, code2) 效率會比一直query好
        box = {
                "type"  : "button",
                "action": {
                    "type"  : "postback",
                    "label" : f"{company.business_entity}",
                    "data"  : f"company&{company.id}"
                },
                "height": "sm"
        }
        FavoriteFlexMessage["body"]["contents"].append(box)
    line_bot_api.reply_message(reply_token, FlexSendMessage('Favorite Info', FavoriteFlexMessage))
        
    


#### 複數公司選擇版面 TODO: 棄用stock物件，改為使用company物件
def multiple_result_output(reply_token, keyword, companies): # companies是Stock物件

    # 載入Flex template
    FlexMessage = json.load(open('templates/template.json','r',encoding='utf-8'))
    FlexMessage['contents'][0]['header']['contents'][0]['text'] = keyword
    candidates_list = []

    for company in companies:
        if company.stock_uniid is None:
            result = api.get_uniid_by_name(company.stock_full_name)
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
                "data": f"stock&{company.id}"
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


#### 複數公司選擇版面 
def multiple_result_output_2(reply_token, keyword, companies): # 參數companies使用company物件

    # 載入Flex template
    FlexMessage = json.load(open('templates/template.json','r',encoding='utf-8'))
    FlexMessage['contents'][0]['header']['contents'][0]['text'] = keyword
    candidates_list = []

    for i in range(len(companies) if len(companies) <= 10 else 10):
        if len(companies[i].business_entity) >= 10:
            business_entity_1 = companies[i].business_entity[:10]
            business_entity_2 = companies[i].business_entity[10:]
            cand_1 =  {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": f"{business_entity_1}",
                    "data": f"company&{companies[i].id}"
                }
            }
            candidates_list.append(cand_1)
            if len(business_entity_2) > 0:
                cand_2 =  {
                    "type": "button",
                    "action": {
                        "type": "postback",
                        "label": f"{business_entity_2}",
                        "data": f"company&{companies[i].id}"
                    }
                }
                seperator = {
                    "type": "separator"
                }
                candidates_list.append(cand_2)
                candidates_list.append(seperator)
        else:
            cand =  {
                "type": "button",
                "action": {
                    "type": "postback",
                    "label": f"{companies[i].business_entity}",
                    "data": f"company&{companies[i].id}"
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
        if sys.argv[1] is not False:
            debug = sys.argv[1]

    # 爬蟲執行時間
    target_time = [13, 30]
    
    _thread.start_new_thread(crawler, (target_time[0], target_time[1], db, debug, app))
    port = int(os.environ.get('PORT', config.port))
    app.run(host='0.0.0.0', port=port, debug=True)
    