import time
import datetime

Starttime = "2021-09-18 00:00"
EndTime = time.strftime("%Y-%m-%d 23:59", time.localtime())
yesterdayTime = (datetime.datetime.now()- datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:00")