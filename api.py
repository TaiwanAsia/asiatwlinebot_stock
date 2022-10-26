import requests, json

# 此處function皆用於搜尋網路資源

# 用統一編號 找 公司
def get_company_by_uniid(uniid):
    print(f"\n ------------ 統一編號找公司  {uniid} ------------")
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


# 用公司名稱 找 公司統一編號
def get_uniid_by_name(company_name):
    if not company_name:
        return False
    url  = requests.get("https://company.g0v.ronny.tw/api/search?q={0}".format(company_name))
    text = url.text
    json_obj = json.loads(text)
    if not json_obj['data']:
        return False
    for candidate in json_obj['data']: # 如有公司名稱部分重複，精準找出目標公司
        company_uni_id = candidate['統一編號']
        if '名稱' in candidate and candidate['名稱'] == company_name:
            company_name = candidate['名稱']
        if '公司名稱' in candidate and candidate['公司名稱'] == company_name:
            company_name = candidate['公司名稱']
    return [company_uni_id, company_name]


# 確認公司股票代號是否存在
def check_code_exist(stock_code):
    url = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?json=1&delay=0&ex_ch=tse_{0}.tw%7C".format(stock_code)
    html  = requests.get(url)
    html_text = html.text
    json_obj = json.loads(html_text)
    if not json_obj['msgArray']:
        return False
    company_name = json_obj['msgArray'][0]['nf']
    stock_code = stock_code
    return [company_name, stock_code]