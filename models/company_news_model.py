from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class Company_news(db.Model):
    __tablename__ = 'company_news'

    id         = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.String, nullable=False)
    company_business_entity = db.Column(db.String, nullable=True)
    keyword      = db.Column(db.String, nullable=False)
    news_title   = db.Column(db.Text, nullable=True)
    news_content = db.Column(db.Text, nullable=True)
    news_url     = db.Column(db.String, nullable=False)
    news_date    = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def find_by_company_id(company_id):
        return Company_news.query.filter_by(company_id=company_id).first()

    def today_update_check_by_company_id(company_id): # 回傳list
        today = datetime.today().date()
        updatedtime_filter = Company_news.updated_at > datetime(today.year, today.month, today.day)
        company_id_filter = Company_news.company_id == company_id
        query = Company_news.query.filter(company_id_filter, updatedtime_filter)
        return query.limit(15).all()

    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<company_news %r    %r  %r>' % (self.keyword, self.news_title, self.news_date)