from .shared_db_model import db
from .dataset_day_model import Dataset_day
from api import get_company_by_uniid
from common.logging import setup_logging
import logging

logDir = 'company'
loggerName = logDir+'allLogger'
setup_logging(logDir)
logger = logging.getLogger(loggerName)

class Company(db.Model):
    __tablename__ = 'company'

    id                 = db.Column(db.Integer, primary_key=True)
    uniid              = db.Column(db.String, nullable=False)
    top_uniid          = db.Column(db.String, nullable=True)
    business_entity    = db.Column(db.String(225), nullable=False)
    capital            = db.Column(db.Integer, nullable=False)
    establishment_date = db.Column(db.String, nullable=False)
    company_type       = db.Column(db.String, nullable=False)
    business_code      = db.Column(db.String(10), nullable=False)
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

    def find_by_business_code(code):
        filter = Company.business_code.like('%{}%'.format(code))
        query  = Company.query.filter(filter)
        return query.all()

    def find_by_business_entity_like_search(business_entity):
        # 優先選擇Dataset_day符合的公司
        cand = Dataset_day.find_by_company_name(business_entity)
        if cand is not None:
            filter = Company.business_entity.like('%{}%'.format(cand.company_name.split('\xa0')[0]))
            query  = Company.query.filter(filter)
        else:
            filter = Company.business_entity.like('%{}%'.format(business_entity)) 
            query  = Company.query.filter(filter)
        return query.all()

    def get_business_code(self) -> str:
        self.update_business_code()
        return self.business_code.split(",")

    def update_business_code(self):
        if self.business_code is None:
            bc_list = []
            company_api_data = get_company_by_uniid(self.uniid)
            if company_api_data:
                company_api_data_business_code = company_api_data['所營事業資料']
                for bc in company_api_data_business_code:
                    if bc[0] != "":
                        bc_list.append(bc[0])
                self.business_code = ','.join(bc_list)
                db.session.commit()
                logger.info(f'{self.business_entity} 更新營業項目代碼: {self.business_code}')
