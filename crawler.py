import urllib.request, requests, time, json, string
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from bs4 import BeautifulSoup
from models.dataset_day_model import Dataset_day
from models.stock_model import Stock

from models.stock_news_model import Stock_news
from models.company_news_model import Company_news
from models.shared_db_model import db
from api import get_uniid_by_name
from common.logging import setup_logging
import logging



logDir = 'crawler'
loggerName = logDir+'allLogger'
setup_logging(logDir)
logger = logging.getLogger(loggerName)



#####  爬蟲
def crawler(target_hour, target_minute, db, debugging, app):

    while 1 == 1:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        now = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區

        if (now.hour == target_hour and now.minute == target_minute) or debugging:
            time.sleep(1)

            print("\n\n*****  CRAWLING...  *****",now,"\n")

            

            if debugging == 2:
                parse_company(db, app)          # 清空Stock表，爬證交所公司資料

            parse_company_price(db, app)    # 爬必富網股價

            parse_company_fullname(db, app) # 更新全名、統一編號

            debugging = False

        

        time.sleep(58)







def parse_company(db, app):

    logger.info('Start Running [parse_company].')

    with app.app_context():

        try:
            sql = "TRUNCATE `linebot_stock`.`stock`;" # Clear data
            db.engine.execute(sql)
            logger.info('Clear table `stock` Successfully.')
        except Exception as e:
            db.session.rollback()
            print(e)
            logger.error('Clear table `stock` Failed. ' + e)


        ##### 1 未上市、櫃公司
        print(f"\n ------------ 爬蟲開始: 未上市、櫃公司 ------------")
        logger.info('Start crawling: 未上市、櫃公司')

        url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=1'
        print(f" ------------ 目標網址: {url} ------------")
        html = requests.get(url)
        html.encoding = "MS950"
        res_html = html.text
        soup = BeautifulSoup(res_html, 'html.parser')
        target_table = soup.select_one("table.h4") # Locate data
        target_trs = target_table.find_all('tr')

        
        for tr in target_trs:
            filtered_keyword = ['有價證券代號及名稱', '股票']
            tds = tr.find_all('td')
            col_1 = tds[0].text.strip()
            if len(tds) > 1 and col_1 not in filtered_keyword:
                code = col_1.split("　")[0]
                name = col_1.split("　")[1].replace("臺","台")
                listing_date = tds[2].text.strip()
                category = tds[4].text.strip()
                insert_data = {'stock_code': code, 'stock_name': name, 'stock_full_name': '', 'listing_date': listing_date, 'stock_type': 1, 'category': category}
                new_stock = Stock(**insert_data)
                db.session.add(new_stock)
        try:                  
            db.session.commit()
            # logger.info('Insert table `stock` Successfully.')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Insert table `stock` Failed. - {name} " + e)

        time.sleep(2)

        ##### 2 上市、櫃公司
        print(f"\n ------------ 爬蟲開始: 上市、櫃公司 ------------")
        logger.info('Start crawling: 上市、櫃公司')

        url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
        print(f" ------------ 目標網址: {url} ------------")
        html = requests.get(url)
        html.encoding = "MS950"
        res_html = html.text
        soup = BeautifulSoup(res_html, 'html.parser')
        target_table = soup.select_one("table.h4") # Locate data
        target_trs = target_table.find_all('tr')
        for tr in target_trs:
            filtered_keyword = ['有價證券代號及名稱', '股票']
            tds = tr.find_all('td')
            col_1 = tds[0].text.strip()
            if col_1 == '上市認購(售)權證':
                break
            if len(tds) > 1 and col_1 not in filtered_keyword:
                code = col_1.split("　")[0]
                name = col_1.split("　")[1].replace("臺","台")
                listing_date = tds[2].text.strip()
                category = tds[4].text.strip()
                insert_data = {'stock_code': code, 'stock_name': name, 'stock_full_name': '', 'listing_date': listing_date, 'stock_type': 2, 'category': category}
                new_stock = Stock(**insert_data)
                db.session.add(new_stock)
        try:                  
            db.session.commit()
            # logger.info('Insert table `stock` Successfully.')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Insert table `stock` Failed. - {name}' + e)



def parse_company_price(db, app):
    ##### 3 未上市股價

    with app.app_context():
        try:
            sql = "TRUNCATE `linebot_stock`.`dataset_day`;" # Clear data
            db.engine.execute(sql)
            logger.info('Clear table `stock` Successfully.')
        except Exception as e:
            db.session.rollback()
            print(e)
            logger.error('Clear table `stock` Failed. ' + e)

        #### 3.1 必富網熱門 Top100
        print(f"\n ------------ 爬蟲開始: 必富網熱門Top100 ------------")
        logger.info('------------ 爬蟲開始: 必富網熱門Top100 ------------')
        website_id = 1
        fp = urllib.request.urlopen('https://www.berich.com.tw/DP/OrderList/List_Hot.asp').read()
        text = fp.decode('Big5')
        soup = BeautifulSoup(text, features='html.parser')
        target_table = soup.select_one('.sin_title').find_parent('table') # Find data
        target_trs = target_table.find_all('tr')
        dataset = [] # Set data
        for tr in target_trs:
            td = tr.find_all('td')
            row = [i.text for i in td]
            dataset.append(row)
        dataset[0][0]  = 'order'
        dataset[0][6]  = '買昨均'
        dataset[0][7]  = '買漲跌幅'
        dataset[0][12] = '賣昨均'
        dataset[0][13] = '賣漲跌幅'
        dataset_list = []
        for data in dataset:
            if data[0] and data[0] != 'order':
                dataset_list.append(dict(zip(dataset[0], data)))
        for dataset in dataset_list:
            dataset['未上市櫃股票公司名稱'] = dataset['未上市櫃股票公司名稱'].replace("臺","台")
            newInput = Dataset_day(website_id=website_id, table_name='hotTop100', order=dataset['order'],
            company_name=dataset['未上市櫃股票公司名稱'], buy_amount=dataset['★買張'], buy_high=dataset['買高'], buy_low=dataset['買低']
            , buy_average=dataset['買均'], buy_average_yesterday=dataset['買昨均'], buy_change_percent=dataset['買漲跌幅'], sell_amount=dataset['★賣張']
            , sell_high=dataset['賣高'], sell_low=dataset['賣低'], sell_average=dataset['賣均'],
            sell_average_yesterday=dataset['賣昨均'], sell_change_percent=dataset['賣漲跌幅'])
            try:
                db.session.add(newInput)
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                print(e)
                logger.error(f'Insert table `Dataset_day` Failed. - {dataset["未上市櫃股票公司名稱"]} ' + e)
        # logger.info('Insert table `Dataset_day` Successfully.')

        print(f"\n ------------ 爬蟲結束: 必富網熱門Top100 ------------")
        logger.info('------------ 爬蟲結束: 必富網熱門Top100 ------------')


    # ##### 3.2 台灣投資達人熱門 Top100
    # print(f"\n ------------ 爬蟲開始: 台灣投資達人熱門Top100 ------------")
    # website_id = 2
    # body = urllib.request.urlopen('http://www.money568.com.tw/Order_Hot.asp').read()
    # soup = BeautifulSoup(body, features='html.parser')
    # target_table = soup.select_one("table.order_table_dv") # Locate data
    # target_trs = target_table.find_all('tr')
    # dataset = [] # Set data
    # for idx, tr in enumerate(target_trs):
    #     if idx > 0 and idx <= 100:
    #         td = tr.find_all('td')
    #         row = [i.text for i in td]
    #         dataset.append(row)
    # for idx, data in enumerate(dataset):
    #     data[1] = data[1].replace("臺","台")
    #     newInput = Dataset_day(website_id=website_id, table_name='hotTop100', order=idx, company_name=data[1],
    #         buy_amount=data[5], buy_average=data[2], buy_average_yesterday=data[3], buy_change_percent=data[4],
    #         sell_amount=data[9], sell_average=data[6], sell_average_yesterday=data[7], sell_change_percent=data[8])
    #     db.session.add(newInput)
    #     db.session.commit()
    
    # print(f"\n ------------ 爬蟲結束: 台灣投資達人熱門Top100 ------------")




def parse_company_fullname(db, app):
    ##### 4 更新上市、未上市公司全名
    

    with app.app_context():

        print(f"\n ------------ 爬蟲開始: 更新上市公司全名 ------------")

        sql = "SET SQL_SAFE_UPDATES=0"
        db.engine.execute(sql)
        stocks = Stock.query.filter_by(stock_type=2)
        target_url = ''
        urls = []
        count = 0
        for stock in stocks:
            count += 1
            url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C"
            position1 = url.find("tse_")
            position2 = url.rfind(".tw")
            target = f"tse_{stock.stock_code}.tw|"
            target_url += target
            if count % 50 == 0:
                target_url = target_url.strip()
                target_url = target_url[:-4]
                new_url = url[:position1] + target_url + url[position2:]
                urls.append(new_url)
                target_url= ''
        print(f" ------------   共{len(urls)}批  送出請求   ------------ ")
        for index, url in enumerate(urls):
            print(f" ------------   第{index}批  送出請求   ------------ ")
            url  = requests.get(url)
            text = url.text
            try:
                json_obj = json.loads(text)
            except Exception as e:
                logger.error('JSON error: ')
                logger.error(e)
            print(f" ------------   第{index}批  寫入資料庫   ------------ ")
            for cmp in json_obj['msgArray']:
                if 'nf' in cmp:
                    stock_full_name = cmp['nf'].replace("臺","台")
                stock_code = cmp['c']
                sql = f"UPDATE stock SET stock_full_name = '{stock_full_name}' WHERE stock_code = '{stock_code}'"
                try:
                    db.engine.execute(sql)        
                except Exception as e:
                    db.session.rollback()
                    print(e)
                    logger.error(f'Update table `stock` Failed. - {stock_code} ' + e)
            # logger.info(f'Update table `stock` - 1 ({index}) Successfully.')

            time.sleep(10) # 以防被鎖IP
        print(f" ------------ 爬蟲結束: 更新上市公司全名 ------------")


        print(f"\n ------------ 爬蟲開始: 更新公司統一編號、全名 ------------")

        companies = Dataset_day.query.filter_by(website_id=1).all()
        for company in companies:
            name = company.company_name.split("\xa0")[0]
            time.sleep(0.1)
            result = get_uniid_by_name(name)
            if result:
                uniid, stock_full_name = result
                count, target = Stock.find_by_name(name[:2], 1)
                if count > 1:
                    count, target = Stock.find_by_name(name[:3], 1)
                if count == 1:
                    sql = f"UPDATE stock SET stock_full_name = '{stock_full_name}', stock_uniid = '{uniid}' WHERE id = '{target[0].id}'"
                    try:
                        db.engine.execute(sql)
                    except Exception as e:
                        db.session.rollback()
                        print(e)
                        logger.error(f"Update table `stock` Failed. - {name} " + e)

                    print(f"更新成功！   {target[0].stock_full_name} => {stock_full_name}")
                else:
                    pass
                    # print("Stock中沒有符合的資料。")
        # logger.info('Update table `stock` - 2 Successfully.')

        print(f" ------------ 爬蟲結束: 更新公司統一編號、全名 ------------")





# 鉅亨網
#######################################  鉅亨網新聞  #######################################
def parse_cnyesNews(company_id, company_business_entity):

    print(f"\n ------------ 爬蟲開始: 鉅亨網 {company_id} {company_business_entity} ------------")
    logger.info(f"------------ 爬蟲開始: 鉅亨網 {company_id} {company_business_entity} ------------")

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # ------  Chrome有更新時
    # 1. 前往https://sites.google.com/chromium.org/driver/downloads?authuser=0 下載與電腦chrome對應的driver版本
    # 2. 將下載解壓縮後的 chromedriver.exe 放到以下路徑
    s = Service(r"C:\Program Files\Google\Chrome\Application\chromedriver.exe") # selenium 瀏覽器選項配置
    
    
    chrome_options = Options()
    chrome_options.use_chromium = True
    chrome_options.add_argument("headless")

    try:
        browser = webdriver.Chrome(options=chrome_options, service=s) # 初始化 webdriver
    except Exception as e:
        logger.error(e)
        return
    browser.maximize_window()
    # url = f'https://www.cnyes.com/search/news?keyword={company_name}' # 另一個頁面，也可撈
    replace_string = ['股份', '有限', '公司']
    for s in replace_string:
        company_name = company_business_entity.replace(s, "")
    common_name = ['台灣', '臺灣', '中華', '中國', '台中', '臺中', '台北', '臺北']
    if not company_name[:2] in common_name:
        keyword = company_name[:2]
    else:
        if len(company_name) > 3:
            keyword = company_name[:4]
        elif len(company_name) == 3:
            keyword = company_name[:3]
        else:
            keyword = company_name[:2]

    print(f" ------------ 爬蟲開始: 關鍵字: {keyword} ------------")
    logger.info(f"------------ 爬蟲開始: 關鍵字: {keyword} ------------")

    url = f'https://news.cnyes.com/search?q={keyword}' # 取得網頁內容
    url = quote(url, safe=string.printable)
    browser.get(url)
    time.sleep(2)
    res = browser.page_source
    soup = BeautifulSoup(res, features='html.parser')
    # prettyHtml = soup.prettify()
    # soup = BeautifulSoup(res, 'lxml')
    articles = soup.find_all('article')
    list_added = []
    
    for article in articles:
        childrens = article.findChildren(recursive=False)
        for child in childrens:
            dt = ''
            if child.get('title') is not None:
                title = child.get('title')
                href  = "https://news.cnyes.com"+child.get('href')
            if child.get('datetime') is not None:
                dt = child.get('datetime').split('T')[0]
            if title and href and dt:
                title = title.replace("<mark>","")
                title = title.replace("</mark>","")
                # if len(stock_code) < 1:
                    # stock_code = company_name
                list_added.append(Company_news(company_id=company_id, company_business_entity=company_business_entity, keyword=keyword, news_title=title, news_url=href, news_date=dt))

    if len(articles) < 1: # 該股無新聞則插入空資料
        print("\n插入空資料")
        list_added.append(Company_news(company_id=company_id, company_business_entity=company_business_entity, keyword=keyword, news_title='', news_url='', news_date='1980-01-01'))

    try:
        db.session.add_all(list_added)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error('Insert table `Stock_news` Failed. ' + e)

    print(f"\n ------------ 爬蟲結束: 鉅亨網 {company_business_entity} ------------")
