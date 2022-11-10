from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class User_favorite_stock(db.Model):
    __tablename__ = 'user_favorite_stock'

    id          = db.Column(db.Integer, primary_key=True)
    user_userid = db.Column(db.String(225), nullable=False)
    stock_ids    = db.Column(db.Text, nullable=False)
    updated_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))


    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<user_favorite_stock  %r   %r>' % (self.user_userid, self.stock_ids)



    def find_by_userid(userid):
        data = User_favorite_stock.query.filter_by(user_userid=userid).first()
        if data:
            return data
        else:
            return False