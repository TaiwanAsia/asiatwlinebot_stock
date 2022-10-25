from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class Stock_news(db.Model):
    __tablename__ = 'stock_news'

    id           = db.Column(db.Integer, primary_key=True)
    stock_code   = db.Column(db.String, nullable=False)
    stock_name   = db.Column(db.String, nullable=True)
    stock_news_title   = db.Column(db.String, nullable=True)
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

    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<Stock_news %r>' % self.stock_code