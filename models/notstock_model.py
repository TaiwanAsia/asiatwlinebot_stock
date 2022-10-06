from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class Notstock(db.Model):
    __tablename__ = 'notstock'

    id            = db.Column(db.Integer, primary_key=True)
    notstock_code = db.Column(db.Text, nullable=False)
    notstock_name = db.Column(db.Text, nullable=False)
    listing_date  = db.Column(db.Date, nullable=False)
    category      = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    
    def __init__(self, notstock_code, notstock_name, listing_date, category):
        self.notstock_code = notstock_code
        self.notstock_name = notstock_name
        self.listing_date  = listing_date
        self.category = category

    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<Notstock %r>' % self.notstock