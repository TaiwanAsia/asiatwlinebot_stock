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
    def __repr__(self):
        return '<Dataset_day %r>' % self.dataset_day