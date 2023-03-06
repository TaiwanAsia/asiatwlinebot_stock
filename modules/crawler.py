import urllib.request, time, string
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from bs4 import BeautifulSoup
from models import db, Dataset_day, Company_news
from modules.logging import setup_logging
import logging

logDir = 'crawler'
loggerName = logDir+'allLogger'
setup_logging(logDir)
logger = logging.getLogger(loggerName)

#  爬蟲
def crawler(target_hour, target_minute, db, debug_mode, app):
    while 1 == 1:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        now = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
        if (now.hour == target_hour and now.minute == target_minute) or debug_mode:
            time.sleep(1)
            print("\n\n***** CRAWLING *****",now,"\n")
            parse_company_price(db, app)    # 爬必富網股價
            debug_mode = False
        time.sleep(58)


# 未上市股價
def parse_company_price(db, app):
    with app.app_context():
        try:
            sql = "TRUNCATE `linebot_stock`.`dataset_day`;" # Clear data
            db.engine.execute(sql)
            logger.info('Clear table `stock` Successfully.')
        except Exception as e:
            db.session.rollback()
            print(e)
            logger.error('Clear table `stock` Failed. ' + e)
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
        print(f"\n ------------ 爬蟲結束: 必富網熱門Top100 ------------")
        logger.info('------------ 爬蟲結束: 必富網熱門Top100 ------------')



# 鉅亨網新聞
def parse_cnyesNews(company_id='', company_business_entity='', keyword=''):

    print(f"\n ------------ 爬蟲開始: 鉅亨網 {company_id} {company_business_entity} {keyword} ------------")
    logger.info(f"------------ 爬蟲開始: 鉅亨網 {company_id} {company_business_entity} {keyword} ------------")

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

    if keyword == '':
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
