from .shared_db_model import db

class Company(db.Model):
    __tablename__ = 'company'

    id                 = db.Column(db.Integer, primary_key=True)
    uniid              = db.Column(db.String, nullable=False)
    top_uniid          = db.Column(db.String, nullable=True)
    business_entity    = db.Column(db.String(225), nullable=False)
    capital            = db.Column(db.Integer, nullable=False)
    establishment_date = db.Column(db.String, nullable=False)
    company_type       = db.Column(db.String, nullable=False)
    industrial_classification_1 = db.Column(db.String, nullable=False)
    industrial_name_1  = db.Column(db.String, nullable=False)
    industrial_classification_2 = db.Column(db.String, nullable=True)
    industrial_name_2  = db.Column(db.String, nullable=True)
    industrial_classification_3 = db.Column(db.String, nullable=True)
    industrial_name_3  = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Company %r  %r %r %r>' % (self.business_entity, self.uniid, self.company_type, self.industrial_name_1)


    def find_by_uniid(uniid):
        return Company.query.filter_by(uniid=uniid).first()

    def find_by_entity(business_entity):
        return Company.query.filter_by(business_entity=business_entity).first()