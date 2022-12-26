from .shared_db_model import db

### 資料來源:
#
#   https://rank.twincn.com/c.aspx
#   行業代號.csv
#   用Toad匯入 https://softfamous.com/toad-for-mysql/

class Industry(db.Model):
    __tablename__ = 'industry'

    id    = db.Column(db.Integer, primary_key=True)
    code  = db.Column(db.String, nullable=False)
    name  = db.Column(db.String, nullable=True)
    upstream_1   = db.Column(db.String, nullable=True)
    upstream_2   = db.Column(db.String, nullable=True)
    downstream_1 = db.Column(db.String, nullable=True)
    downstream_2 = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Industry %r  %r %r>' % (self.id, self.code, self.name)


    def get_by_code(code):
        return Industry.query.filter_by(code=code).first()

    def get_by_name_like(keyword):
        name_filter = Industry.name.like('%{}%'.format(keyword))
        query = Industry.query.filter(name_filter)
        return query.all()

    def update_stream(id, stream, stream_id):
        Industry.query.filter(Industry.id == id).update({stream : stream_id})
        db.session.commit()
        # pass