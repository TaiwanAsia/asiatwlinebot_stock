from models.shared_db_model import db
from models.stock_model import Stock

# 此處function皆用於搜尋資料庫


# 用公司名稱 找 股票代號
def get_company_by_name(name):
    if name:
        company = Stock.find_by_fullname(name) # 先搜尋全名
        
        if company is None:
            company = Stock.find_by_name(name) # 再搜尋簡稱
        
        if company is not None:
            return company

        
    return False

        
        

