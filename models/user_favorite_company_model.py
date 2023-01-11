from datetime import datetime, timedelta, timezone
from .shared_db_model import db

class User_favorite_company(db.Model):
    __tablename__ = 'user_favorite_company'

    id     = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(225), nullable=False)
    company_ids = db.Column(db.Text, nullable=False)
    updated_at  = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))


    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<user_favorite_company  %r   %r>' % (self.userid, self.company_ids)



    def find_by_userid(userid):
        return User_favorite_company.query.filter_by(userid=userid).first()
        