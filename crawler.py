from datetime import datetime, timedelta, timezone
import urllib.request
import time
from bs4 import BeautifulSoup
from models.dataset_day import Dataset_day



#################################  爬蟲
def crawler(target_hour, target_minute, db):
    while 1 == 1:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        now = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
        if now.hour == target_hour and now.minute == target_minute:
            print(now)

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