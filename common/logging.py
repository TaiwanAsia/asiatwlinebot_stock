import logging
from datetime import datetime, timedelta, timezone
import os


def setup_logging(logDir):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    now = dt1.astimezone(timezone(timedelta(hours=8))) # 轉換時區 -> 東八區
    date_today = datetime.strftime(now, '%Y-%m-%d')
    
    logName = date_today + '.log'
    # logDir  = 'log'
    logPath = 'log/' + logDir + '/' + logName

    os.makedirs('log/' + logDir,exist_ok=True)

    allLogger = logging.getLogger(logDir+'allLogger')
    allLogger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler(logPath, encoding='utf-8',mode='a')
    fileHandler.setLevel(logging.INFO)

    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.WARNING)

    AllFormatter = logging.Formatter("%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s")
    fileHandler.setFormatter(AllFormatter)
    streamHandler.setFormatter(AllFormatter)

    allLogger.addHandler(fileHandler)
    allLogger.addHandler(streamHandler)

    return allLogger
