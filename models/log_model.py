from .shared_db_model import db

class Log(db.Model):
    __tablename__ = 'log'

    id              = db.Column(db.Integer, primary_key=True)
    user            = db.Column(db.String(45), db.ForeignKey('user.id'))
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

    # def update_stream(id, stream, stream_id):
    #     Business_code.query.filter(Business_code.id == id).update({stream : stream_id})
    #     db.session.commit()