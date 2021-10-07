# -*- coding:utf-8 -*-
from config import user
import time
import pymysql


def clock_in(mobile, password):
    student = user(mobile, password)
    login = student.login()
    if login['response'] != 100:
        print(mobile + ":" + login['message'])
        return False
    try:
        student.Headers['loginToken'] = login['data']['access_token']
    except Exception as e:
        print(e)
        print(mobile + ":" + "access_token no")
        return False
    select_xbh = student.select_xbh()
    if select_xbh['response'] != 100:
        print(mobile + ":" + select_xbh['message'])
        return False
    for i in select_xbh['data']['hotApps']:
        if u"校本化" in i['name']:
            access = student.access_xbh(i['url'])
            if access == False:
                ss = student.shouquan()  # 解决了点击校本化需要申请授权的Bug
                student.access_xbh(i['url'])
            break
    message = student.select_today_task()
    try:
        for i in message["data"]:
            if time.strftime("%Y-%m-%d", time.localtime()) in i["Title"]:
                today_data = student.today_task(i['TaskId'])
                if today_data['code'] == 0:
                    print(mobile + " 今日打卡成功")
                    return True
                else:
                    print(mobile + " 今日打卡失败")
                    return False
        print(mobile + " 今日无打卡或您已经打卡了")
        return False
    except Exception as e:
        print(e)
        print(mobile + " 今日无打卡或您已经打卡了")
        return False


def main():
    db = pymysql.connect(host='localhost', user='username', password='password', database='yiban')
    cursor = db.cursor()
    sql = "SELECT mobile, password FROM `students`"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for user_text in results:
            try:
                clock_in(user_text[0], user_text[1])
                time.sleep(0.1)
            except Exception as e:
                print(e)  # 尝试判断未知错误
                time.sleep(0.1)
    except Exception as e:
        print(e)  # 尝试判断未知错误
    db.close()


if __name__ == '__main__':
    print(time.strftime("开始打卡 %Y-%m-%d %H:%M:%S", time.localtime()))
    Start = time.time()
    main()
    print(time.strftime("打卡结束 %Y-%m-%d %H:%M:%S", time.localtime()))
    print("总耗时: {}s".format(time.time() - Start))  # 计时
