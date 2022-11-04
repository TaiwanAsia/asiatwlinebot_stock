from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class Stock_news(db.Model):
    __tablename__ = 'stock_news'

    id           = db.Column(db.Integer, primary_key=True)
    stock_code   = db.Column(db.String, nullable=False)
    stock_name   = db.Column(db.String, nullable=True)
    stock_news_title   = db.Column(db.Text, nullable=True)
    stock_news_content = db.Column(db.Text, nullable=True)
    stock_news_url     = db.Column(db.String, nullable=False)
    stock_news_date    = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def find_by_code(code):
        return Stock_news.query.filter_by(stock_code=code).first()

    def today_update_check(code, name=''):
        today = datetime.today().date()
        code_filter = Stock_news.stock_code == code
        updatedtime_filter = Stock_news.updated_at > datetime(today.year, today.month, today.day)
        if len(code) < 1:
            name_filter = Stock_news.stock_name.like('%{}%'.format(name))
            query = Stock_news.query.filter(code_filter, name_filter, updatedtime_filter)
        else:
            query = Stock_news.query.filter(code_filter, updatedtime_filter)
        return query.limit(15).all()

    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<Stock_news %r  %r>' % (self.stock_news_title, self.stock_news_date)