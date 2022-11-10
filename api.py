import requests, json
from models.stock_model import Stock
from models.shared_db_model import db

# 此處function皆用於搜尋"網路資源"

# 用統一編號 找 公司
def get_company_by_uniid(uniid):
    print(f" ------------ 統一編號找公司  {uniid} ------------")
    url      = requests.get("https://company.g0v.ronny.tw/api/show/{0}".format(uniid))
    text     = url.text
    json_obj = json.loads(text)
    if '名稱' in json_obj['data']:
        company_name   = json_obj['data']['名稱']
    elif '公司名稱' in json_obj['data']:
        company_name = json_obj['data']['公司名稱']
    else:
        return False
    return company_name


# 用公司名稱 找 統一編號
def get_uniid_by_name(stock_full_name):
    print(f" ------------ 公司名稱查詢統一編號  {stock_full_name} ------------")
    if not stock_full_name:
        return False
    uniid = ''
    url    = "https://company.g0v.ronny.tw/api/search?q={0}".format(stock_full_name)
    result = requests.get(url)
    text   = result.text
    json_obj = json.loads(text)
    if not json_obj['data']:
        return False
    for candidate in json_obj['data']: # 如有公司名稱部分重複，精準找出目標公司
        if '商業名稱' in candidate:
            continue
        uniid = candidate['統一編號'] # 有資料就先取，再來才判斷公司精準與否
        stock_full_name = candidate['名稱'] if '名稱' in candidate else candidate['公司名稱']
        if '名稱' in candidate and candidate['名稱'] == stock_full_name:
            stock_full_name = candidate['名稱']
            uniid = candidate['統一編號']
        if '公司名稱' in candidate and candidate['公司名稱'] == stock_full_name:
            stock_full_name = candidate['公司名稱']
            uniid = candidate['統一編號']
    return [uniid,stock_full_name]


# 確認公司股票代號是否存在
def check_code_exist(stock_code):
    print(f" ------------ 股票代號查詢公司  {stock_code} ------------")
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C".format(stock_code)
    html  = requests.get(url)
    html_text = html.text
    json_obj = json.loads(html_text)
    if not json_obj['msgArray']:
        return False
    company_name = json_obj['msgArray'][0]['nf']
    stock_code = stock_code
    return [company_name, stock_code]


# 關鍵字找公司名稱
def parse_by_keyword(keyword):
    print(f"\n ------------ 資料庫無資料，爬蟲關鍵字找公司名稱 : {keyword} ------------")
    url = f"https://data.gcis.nat.gov.tw/od/data/api/6BBA2268-1367-4B42-9CCA-BC17499EBE8C?$format=json&$filter=Company_Name like {keyword} and Company_Status eq 01&$skip=0&$top=50"
    html  = requests.get(url)
    html_text = html.text
    json_obj = json.loads(html_text)

    if len(json_obj) < 0:
        return 0, None

    for cmp in json_obj:
        if cmp['Company_Name'].find("股份") > 0:
            full_name = cmp['Company_Name']
            name = cmp['Company_Name'][:3]
            uniid = cmp['Business_Accounting_NO']
            # 重要
            # 在此預設 stock_type=1
            newInput = Stock(stock_code='', stock_full_name=full_name, stock_name=name, stock_uniid=uniid, listing_date='1985-09-05', stock_type=1, category='') 
            db.session.add(newInput)
            db.session.commit()

    count, company = Stock.find_by_name(keyword)
    
    return count, company
    
