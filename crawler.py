from datetime import datetime, timedelta, timezone
import urllib.request, requests, time, json
from bs4 import BeautifulSoup
from models.dataset_day_model import Dataset_day
from models.stock_model import Stock
from models.notstock_model import Notstock



#################################  爬蟲
def crawler(target_hour, target_minute, db, debuging, app):
    while 1 == 1:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        now = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區

        if (now.hour == target_hour and now.minute == target_minute) or debuging:
            print("\n*****  crawling...  *****")
            print(now,"\n")

            ##### 未上市、櫃公司
            url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=1'
            html = requests.get(url)
            html.encoding = "MS950"
            res_html = html.text
            soup = BeautifulSoup(res_html, 'html.parser')

            # Locate data
            target_table = soup.select_one("table.h4")
            target_trs = target_table.find_all('tr')

            # Clear data
            try:
                sql = "TRUNCATE `linebot_stock`.`notstock`;"
                db.engine.execute(sql)
            except:
                db.session.rollback()

            for tr in target_trs:
                filtered_keyword = ['有價證券代號及名稱', '股票']
                tds = tr.find_all('td')
                col_1 = tds[0].text.strip()

                if len(tds) > 1 and col_1 not in filtered_keyword:
                    code = col_1.split("　")[0]
                    name = col_1.split("　")[1]
                    listing_date = tds[2].text.strip()
                    category = tds[4].text.strip()
                    insert_data = {'notstock_code': code, 'notstock_name': name, 'listing_date': listing_date, 'category': category}
                    new_stock = Notstock(**insert_data)
                    db.session.add(new_stock)
            db.session.commit()

            ##### 上市、櫃公司
            url = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
            html = requests.get(url)
            html.encoding = "MS950"
            res_html = html.text
            soup = BeautifulSoup(res_html, 'html.parser')

            # Locate data
            target_table = soup.select_one("table.h4")
            target_trs = target_table.find_all('tr')

            # Clear data
            try:
                sql = "TRUNCATE `linebot_stock`.`stock`;"
                db.engine.execute(sql)
            except:
                db.session.rollback()

            for tr in target_trs:
                filtered_keyword = ['有價證券代號及名稱', '股票']
                tds = tr.find_all('td')
                col_1 = tds[0].text.strip()

                if col_1 == '上市認購(售)權證':
                    break

                if len(tds) > 1 and col_1 not in filtered_keyword:
                    code = col_1.split("　")[0]
                    name = col_1.split("　")[1]
                    listing_date = tds[2].text.strip()
                    category = tds[4].text.strip()
                    insert_data = {'stock_code': code, 'stock_name': name, 'stock_full_name': '', 'listing_date': listing_date, 'category': category}
                    new_stock = Stock(**insert_data)
                    db.session.add(new_stock)
            db.session.commit()
            
            ###################### 未上市股價
            # Clear data
            sql = "TRUNCATE `linebot_stock`.`dataset_day`;"
            db.engine.execute(sql)

            ######  必富網熱門Top100 website_id=1  ######
            print(f"\n ------------ 爬蟲開始: 必富網熱門Top100 ------------")
            website_id = 1
            fp = urllib.request.urlopen('https://www.berich.com.tw/DP/OrderList/List_Hot.asp').read()
            text = fp.decode('Big5')
            soup = BeautifulSoup(text, features='html.parser')

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
            soup = BeautifulSoup(body, features='html.parser')

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


            #####  更新公司全名  #####
            with app.app_context():
                sql = "SELECT `stock_code` FROM `stock`;"
                stock_codes = db.engine.execute(sql).fetchall()
                print(f"\n ------------ 爬蟲開始: 更新上市公司全名 ------------")
                print(f"\n ------------ 預計時間: 190秒 = 3分10秒  ------------")

                target_url = ''
                urls = []
                count = 0

                for stock_code in stock_codes:
                    count += 1

                    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C"
                    position1 = url.find("tse_")
                    position2 = url.rfind(".tw")
                    target = f"tse_{stock_code[0]}.tw|"
                    target_url += target

                    if count % 50 == 0:
                        target_url = target_url.strip()
                        target_url = target_url[:-4]
                        new_url = url[:position1] + target_url + url[position2:]
                        urls.append(new_url)
                        target_url= ''

                for index, url in enumerate(urls):
                    print(f"--------------------   第{index}批  送出請求   --------------------")

                    url  = requests.get(url)
                    text = url.text
                    json_obj = json.loads(text)

                    print(f"--------------------   第{index}批  寫入資料庫   --------------------")
                    for cmp in json_obj['msgArray']:
                        stock_full_name = cmp['nf']
                        stock_code = cmp['c']
                        sql = f"UPDATE stock SET stock_full_name = '{stock_full_name}' WHERE stock_code = '{stock_code}'"
                        db.engine.execute(sql)
                    
                    # 以防被鎖IP
                    time.sleep(10)
                

            time.sleep(58)