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
    industrial_classification   = db.Column(db.String, nullable=False)
    industrial_name    = db.Column(db.String, nullable=False)
    industrial_classification_1 = db.Column(db.String, nullable=False)
    industrial_name_1  = db.Column(db.String, nullable=False)
    industrial_classification_2 = db.Column(db.String, nullable=True)
    industrial_name_2  = db.Column(db.String, nullable=True)
    industrial_classification_3 = db.Column(db.String, nullable=True)
    industrial_name_3  = db.Column(db.String, nullable=True)

    def __repr__(self):
        return '<Company %r  %r %r %r>' % (self.business_entity, self.uniid, self.company_type, self.industrial_name)

    def find_by_id(id):
        return Company.query.filter_by(id=id).first()

    def find_by_ids(ids):
        ids = ids.split(",")
        return Company.query.filter(Company.id.in_(ids)).all()

    def find_by_uniid(uniid):
        return Company.query.filter_by(uniid=uniid).first()

    def find_by_business_entity(business_entity):
        return Company.query.filter_by(business_entity=business_entity).first()

    def find_by_industry(industrial_classification):
        return Company.query.filter_by(industrial_classification=industrial_classification).all()

    def find_by_business_entity_like_search(business_entity, keyword_length = 3): # 模糊搜尋
        filter = Company.business_entity.like('%{}%'.format(business_entity[ : keyword_length]))
        query  = Company.query.filter(filter)
        if query.count() < 1: # 如無資料，則改用keyword前2個字做模糊搜尋
            filter = Company.business_entity.like('%{}%'.format(business_entity[ : 2])) 
            query  = Company.query.filter(filter)
        return query.all()
