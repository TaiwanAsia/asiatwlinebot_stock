from .shared_db_model import db

# 資料來源:
# https://gcis.nat.gov.tw/cod/code_v8.xlsx

class Business_code(db.Model):
    __tablename__ = 'business_code'

    id         = db.Column(db.Integer, primary_key=True)
    code       = db.Column(db.String, nullable=False)
    name_ch    = db.Column(db.String, nullable=True)
    name_en    = db.Column(db.String, nullable=True)
    definition = db.Column(db.Text, nullable=True)
    upstream   = db.Column(db.String, nullable=True)
    downstream = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Business_code %r  %r %r>' % (self.id, self.code, self.name_ch)

    def get_by_code(code):
        return Business_code.query.filter_by(code=code).first()

    def update_stream(id, stream, stream_id):
        Business_code.query.filter(Business_code.id == id).update({stream : stream_id})
        db.session.commit()