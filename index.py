#!/usr/bin/env python
#-*- coding:utf-8 -*-
from config import user
import time

access_xbh = {}

student = user('username','password')
login = student.login()
if login['response'] != 100:
    print(login['message'])
    pass
try:
    student.Headers['loginToken'] = login['data']['access_token']
except:
    pass
select_xbh = student.select_xbh()
if select_xbh['response'] != 100:
    print(select_xbh['message'])
for i in select_xbh['data']['hotApps']:
    if u"校本化" in i['name']:
        access_xbh = student.access_xbh(i['url'])

message = student.select_today_task()
flag = 0
for i in message["data"]:
    if time.strftime("%Y-%m-%d", time.localtime()) in i["Title"]:
        flag += 1
        today_data = student.today_task(message['data'][0]['TaskId'])
        if today_data['code'] == 0:
            print("今日打卡成功")
        else:
            print("今日打卡失败")
if flag == 0:
    print("今日无打卡或您已经打卡了")