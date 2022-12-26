from datetime import datetime, timedelta, timezone
from .shared_db_model import db


class Dataset_day(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    website_id = db.Column(db.Integer, nullable=False)
    table_name = db.Column(db.Text, nullable=False)
    order      = db.Column(db.Integer, nullable=True)
    company_name = db.Column(db.Text, nullable=True)
    buy_amount = db.Column(db.Text, nullable=True)
    buy_high = db.Column(db.Text, nullable=True)
    buy_low = db.Column(db.Text, nullable=True)
    buy_average = db.Column(db.Text, nullable=True)
    buy_average_yesterday = db.Column(db.Text, nullable=True)
    buy_change_percent = db.Column(db.Text, nullable=True)
    sell_amount = db.Column(db.Text, nullable=True)
    sell_high = db.Column(db.Text, nullable=True)
    sell_low = db.Column(db.Text, nullable=True)
    sell_average = db.Column(db.Text, nullable=True)
    sell_average_yesterday = db.Column(db.Text, nullable=True)
    sell_change_percent = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))

    def __init__(self, website_id, table_name, order, company_name, buy_amount, buy_average, buy_average_yesterday, buy_change_percent,
        sell_amount, sell_average, sell_average_yesterday, sell_change_percent, buy_high=None, buy_low=None, sell_high=None, sell_low=None, date=None, updated_at=None):
        self.website_id = website_id
        self.table_name = table_name
        self.order = order
        self.company_name = company_name
        self.buy_amount = buy_amount
        self.buy_high = buy_high
        self.buy_low = buy_low
        self.buy_average = buy_average
        self.buy_average_yesterday = buy_average_yesterday
        self.buy_change_percent = buy_change_percent
        self.sell_amount = sell_amount
        self.sell_high = sell_high
        self.sell_low = sell_low
        self.sell_average = sell_average
        self.sell_average_yesterday = sell_average_yesterday
        self.sell_change_percent = sell_change_percent
        self.date = date
        self.updated_at = updated_at

    def find_by_company_name_like_search(company_name, keyword_length = 3): # 模糊搜尋 預設前3個字
        filter = Dataset_day.company_name.like('%{}%'.format(company_name[ : keyword_length]))
        query  = Dataset_day.query.filter(filter).first()
        if query is None: # 如無資料，則改用keyword前2個字做模糊搜尋
            filter = Dataset_day.company_name.like('%{}%'.format(company_name[ : 2]))
        return Dataset_day.query.filter(filter).first()

    def __repr__(self):
        return '<Dataset_day %r buy_amount: %r buy_average:%r sell_amount:%r sell_average:%r>' % (self.company_name, self.buy_amount, self.buy_average, self.sell_amount, self.sell_average)