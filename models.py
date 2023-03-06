from flask_sqlalchemy import SQLAlchemy
from modules.apis import get_company_by_uniid
from modules.logging import setup_logging
from datetime import datetime, timedelta, timezone
import logging

db = SQLAlchemy()


logDir = 'company'
loggerName = logDir+'allLogger'
setup_logging(logDir)
logger = logging.getLogger(loggerName)



class User(db.Model):
    __tablename__ = 'user'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.String(50), nullable=False)
    is_member   = db.Column(db.String(10), nullable=False, default='no')
    is_admin    = db.Column(db.String(10), nullable=False, default='no')
    text_reply  = db.Column(db.String(10), nullable=False, default='on')
    image_reply = db.Column(db.String(10), nullable=False, default='on')
    file_reply  = db.Column(db.String(10), nullable=False, default='on')
    join_member_time  = db.Column(db.DateTime, nullable=True)
    last_message_time = db.Column(db.DateTime, nullable=True)
    updated_at  = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs) -> None:
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return '<user %r  %r %r>' % (self.id, self.user_id, self.last_message_time)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_by_user_id(user_id):
        return User.query.filter_by(user_id=user_id).first()

    def turn_on_off_text_reply(self, mode):
        self.text_reply = mode        
        db.session.commit()
    
    def turn_on_off_file_reply(self, mode):
        self.file_reply = mode        
        db.session.commit()
    
    def turn_on_off_image_reply(self, mode):
        self.image_reply = mode        
        db.session.commit()


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
        

class Company(db.Model):
    __tablename__ = 'company'

    id                 = db.Column(db.Integer, primary_key=True, index=True)
    uniid              = db.Column(db.String(10), nullable=False)
    top_uniid          = db.Column(db.String(10), nullable=True)
    business_entity    = db.Column(db.String(225), nullable=False)
    capital            = db.Column(db.Integer, nullable=False)
    establishment_date = db.Column(db.String(30), nullable=False)
    company_type       = db.Column(db.String(30), nullable=False)
    business_code      = db.Column(db.TEXT, nullable=True)
    company_news       = db.relationship(
        'Company_news',
        backref='company', # ref 可以讓我們使用 Company_news.company 進行對 company 操作
        lazy='dynamic' # 有使用才載入，提昇效能
    )

    def __init__(self, business_entity, capital, establishment_date, company_type, business_code='', **kwargs) -> None:
        super(Company, self).__init__(**kwargs)
        self.business_entity = business_entity
        self.capital = capital
        self.establishment_date = establishment_date
        self.company_type  = company_type
        self.business_code = business_code

    def __repr__(self):
        return '<Company %r  %r %r %r>' % (self.business_entity, self.uniid, self.top_uniid, self.company_type)

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            logger.exception(e)
    
    def find_by_id(id):
        return Company.query.filter_by(id=id).first()

    def find_by_ids(ids):
        ids = ids.split(",")
        return Company.query.filter(Company.id.in_(ids)).all()

    def find_by_uniid(uniid):
        return Company.query.filter_by(uniid=uniid).first()

    def find_by_business_entity(business_entity):
        return Company.query.filter_by(business_entity=business_entity).first()

    # def find_by_industry(industrial_classification):
    #     return Company.query.filter_by(industrial_classification=industrial_classification).all()

    def find_by_company_type(company_type):
        return Company.query.filter_by(company_type=company_type).all()

    def find_by_business_code(code):
        filter = Company.business_code.like('%{}%'.format(code))
        query  = Company.query.filter(filter)
        return query.all()

    def find_by_business_entity_like_search(business_entity):
        # 優先選擇Dataset_day符合的公司
        cand = Dataset_day.find_by_company_name(business_entity)
        if cand is not None:
            name_filter = Company.business_entity.like('%{}%'.format(cand.company_name.split('\xa0')[0]))
        else:
            name_filter = Company.business_entity.like('%{}%'.format(business_entity))
        # 過濾掉子公司
        topuniid_filter = Company.top_uniid.is_(None)
        query  = Company.query.filter(topuniid_filter, name_filter)
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
                try:
                    db.session.commit()
                except Exception as e:
                    print('更新營業項目代碼失敗。')
                    logger.exception('更新營業項目代碼失敗。')
                    logger.exception(e)
                    return '更新營業項目代碼失敗'
                logger.info(f'{self.business_entity} 更新營業項目代碼: {self.business_code}')
                return 'success'
            else:
                return 'api查無資料'
        else:
            return '已有營業項目代碼'


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

    def __init__(self, website_id, table_name, order, company_name, buy_amount, buy_average, buy_average_yesterday, buy_change_percent,
        sell_amount, sell_average, sell_average_yesterday, sell_change_percent, buy_high=None, buy_low=None, sell_high=None, sell_low=None, date=None, updated_at=None):
        self.website_id = website_id
        self.table_name = table_name
        self.order = order
        self.company_name = company_name
        self.buy_amount = buy_amount
        self.buy_high = buy_high
        self.buy_low = buy_low
        self.buy_average = buy_average
        self.buy_average_yesterday = buy_average_yesterday
        self.buy_change_percent = buy_change_percent
        self.sell_amount = sell_amount
        self.sell_high = sell_high
        self.sell_low = sell_low
        self.sell_average = sell_average
        self.sell_average_yesterday = sell_average_yesterday
        self.sell_change_percent = sell_change_percent
        self.date = date
        self.updated_at = updated_at

    def find_by_id(id):
        return Dataset_day.query.filter_by(id=id).first()

    def find_by_company_name(company_name):
        keyword = company_name.split("股份")[0]
        return Dataset_day.query.filter_by(company_name=keyword).first()

    def find_by_company_name_like_search(company_name, keyword_length = 4): # 模糊搜尋前4個字
        keyword = company_name.split("股份")[0]
        filter = Dataset_day.company_name.like('%{}%'.format(keyword[ : keyword_length]))
        return Dataset_day.query.filter(filter).all()

    def __repr__(self):
        return '<Dataset_day %r buy_amount: %r buy_average:%r sell_amount:%r sell_average:%r>' % (self.company_name, self.buy_amount, self.buy_average, self.sell_amount, self.sell_average)



class Business_code(db.Model):
    __tablename__ = 'business_code'

    id         = db.Column(db.Integer, primary_key=True)
    code       = db.Column(db.String(45), nullable=False)
    name_ch    = db.Column(db.String(45), nullable=True)
    name_en    = db.Column(db.String(45), nullable=True)
    definition = db.Column(db.Text, nullable=True)
    upstream   = db.Column(db.String(45), nullable=True)
    downstream = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return '<Business_code %r  %r %r>' % (self.id, self.code, self.name_ch)

    def get_by_code(code):
        return Business_code.query.filter_by(code=code).first()

    def update_stream(id, stream, stream_id):
        Business_code.query.filter(Business_code.id == id).update({stream : stream_id})
        db.session.commit()

    def get_by_chinese_name(keyword):
        name_filter = Business_code.name_ch.like('%{}%'.format(keyword))
        query = Business_code.query.filter(name_filter)
        return query.all()



class Company_news(db.Model):
    __tablename__ = 'company_news'

    id           = db.Column(db.Integer, primary_key=True)
    company_id   = db.Column(db.Integer, db.ForeignKey('company.id'))
    company_business_entity = db.Column(db.String(45), nullable=True)
    keyword      = db.Column(db.String(15), nullable=False)
    news_title   = db.Column(db.String(400), nullable=True)
    news_content = db.Column(db.Text, nullable=True)
    news_url     = db.Column(db.String(225), nullable=False)
    news_date    = db.Column(db.String(45), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def find_by_company_id(company_id):
        return Company_news.query.filter_by(company_id=company_id).first()

    def today_update_check_by_keyword(keyword):
        today = datetime.today().date()
        updatedtime_filter = Company_news.updated_at > datetime(today.year, today.month, today.day)
        keyword_filter = Company_news.keyword == keyword
        query = Company_news.query.filter(keyword_filter, updatedtime_filter)
        return query.limit(15).all()

    def today_update_check_by_company_id(company_id): # 回傳list
        today = datetime.today().date()
        updatedtime_filter = Company_news.updated_at > datetime(today.year, today.month, today.day)
        company_id_filter = Company_news.company_id == company_id
        query = Company_news.query.filter(company_id_filter, updatedtime_filter)
        return query.limit(15).all()

    # In Python, __repr__ is a special method used to represent a class’s objects as a string.
    def __repr__(self):
        return '<company_news %r    %r  %r>' % (self.keyword, self.news_title, self.news_date)


class Group(db.Model):
    __tablename__ = 'group'

    id          = db.Column(db.Integer, primary_key=True)
    group_id    = db.Column(db.String(50), nullable=False)
    user_ids    = db.Column(db.String(225), nullable=False, default='')
    text_reply  = db.Column(db.String(10), nullable=False, default='on')
    image_reply = db.Column(db.String(10), nullable=False, default='on')
    file_reply  = db.Column(db.String(10), nullable=False, default='on')
    last_message_time = db.Column(db.DateTime, nullable=True)
    updated_at  = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs) -> None:
        super(Group, self).__init__(**kwargs)

    def __repr__(self):
        return '<user %r  %r %r>' % (self.id, self.group_id, self.user_ids)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_by_group_id(group_id):
        return Group.query.filter_by(group_id=group_id).first()

    def turn_on_off_text_reply(self, mode):
        self.text_reply = mode        
        db.session.commit()
    
    def turn_on_off_file_reply(self, mode):
        self.file_reply = mode        
        db.session.commit()
    
    def turn_on_off_image_reply(self, mode):
        self.image_reply = mode        
        db.session.commit()



class Log(db.Model):
    __tablename__ = 'log'

    id              = db.Column(db.Integer, primary_key=True)
    chatroom        = db.Column(db.String(100))
    message_type    = db.Column(db.String(20), nullable=False)
    message_content = db.Column(db.Text, nullable=True)
    created_at      = db.Column(db.DateTime, nullable=True)

    def __init__(self, **kwargs) -> None:
        super(Log, self).__init__(**kwargs)

    def __repr__(self):
        return '\n<log %r  %r  %r  %r>' % (self.id, self.user, self.message_type, self.created_at)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def get_by_user_id(user):
        return Log.query.filter_by(user=user).order_by(Log.created_at).limit(100).all()
        
        