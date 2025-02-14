import requests, json

# 用統一編號 找 公司
def get_company_by_uniid(uniid):
    print(f" ------------ [api] - 統一編號找公司  {uniid} ------------")
    url      = requests.get("https://company.g0v.ronny.tw/api/show/{0}".format(uniid))
    text     = url.text
    json_obj = json.loads(text)
    if '名稱' in json_obj['data']:
        company_data = json_obj['data']
    elif '公司名稱' in json_obj['data']:
        company_data = json_obj['data']
    else:
        return False
    return company_data


# 用公司名稱 找 統一編號
def get_uniid_by_name(stock_full_name):
    print(f" ------------ [api] - 公司名稱查詢統一編號  {stock_full_name} ------------")
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
    print(f" ------------ [api] - 股票代號查詢公司  {stock_code} ------------")
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C".format(stock_code)
    html  = requests.get(url)
    html_text = html.text
    json_obj = json.loads(html_text)
    if not json_obj['msgArray']:
        return False
    company_name = json_obj['msgArray'][0]['nf']
    stock_code = stock_code
    return [company_name, stock_code]