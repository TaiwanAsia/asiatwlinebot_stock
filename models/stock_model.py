from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class Stock(db.Model):
    __tablename__ = 'stock'

    id           = db.Column(db.Integer, primary_key=True)
    stock_code   = db.Column(db.Text, nullable=False)
    stock_name   = db.Column(db.Text, nullable=False)
    stock_full_name   = db.Column(db.Text, nullable=False)
    stock_uniid   = db.Column(db.String(8), nullable=True)
    listing_date = db.Column(db.Date, nullable=False)
    stock_type   = db.Column(db.String(1), nullable=False)
    category     = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    
    def __init__(self, stock_code, stock_name, stock_full_name, listing_date, stock_type, category):
        self.stock_code = stock_code
        self.stock_name = stock_name
        self.stock_full_name = stock_full_name
        self.listing_date = listing_date
        self.stock_type = stock_type
        self.category = category


    def find_by_name(name, type=False):
        print(f" ------------ 依公司簡稱查詢公司 Company_name: {name} ------------")
        if not name:
            return False
        name_filter = Stock.stock_name.like('%{}%'.format(name))
        if type:
            type_filter = Stock.stock_type==type
            query = Stock.query.filter(name_filter, type_filter)
        else:
            query = Stock.query.filter(name_filter)
        count = query.count()
        if count > 1:
            return count
        return query.first()


    def find_by_fullname(name):
        print(f" ------------ 依公司全名查詢公司 Company_name: {name} ------------")
        return Stock.query.filter_by(stock_full_name=name).first()


    def find_by_fullname_like(name, type=False):
        l = len(name)
        print(f" ------------ 依公司全名查詢公司(like) Company_name: {name} length: {l} ------------")
        name_filter = Stock.stock_full_name.like('%{}%'.format(name[:l]))
        if type:
            type_filter = Stock.stock_type==type
            query = Stock.query.filter(name_filter, type_filter)
        else:
            query = Stock.query.filter(name_filter)
        count = query.count()
        if count > 1:
            return count
        return query.first()


    def find_by_code(code):
        data = Stock.query.filter_by(stock_code=code).first()
        return data


    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<Stock %r 簡稱:%r 統編:%r 代號:%r>' % (self.stock_full_name, self.stock_name, self.stock_uniid, self.stock_code)