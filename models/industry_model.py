from .shared_db_model import db


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
        return '<Company %r  %r %r>' % (self.id, self.code, self.name)


    def find_by_code(code):
        return Industry.query.filter_by(code=code).first()
