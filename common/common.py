import os
from models.user_model import User
from models.log_model import Log
from datetime import datetime, timezone, timedelta

def check_user_uploads_folder(user_id):
    if not os.path.isdir('../uploads/'+user_id):
        os.makedirs('./uploads/' + user_id + '/', exist_ok=True)

def get_user(user_id):
    user = User.get_by_user_id(user_id)
    if user is None:
        user = add_user(user_id)
    return user

def add_user(user_id):
    user = User(user_id=user_id, last_message_time=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    user.save()
    return user

def add_log(user, message_type, message_content):
    log_user = Log(user=user.id, message_type=message_type, message_content=message_content, created_at=datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S"))
    log_user.save()