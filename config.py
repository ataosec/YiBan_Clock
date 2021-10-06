#!/usr/bin/env python
#-*- coding:utf-8 -*-
import requests
import random
from Crypto.PublicKey import RSA as RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import re
import times as T
import time

# 登陆时对password进行加密
def encryptPassword(pwd):
    PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
        MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA6aTDM8BhCS8O0wlx2KzA
        Ajffez4G4A/QSnn1ZDuvLRbKBHm0vVBtBhD03QUnnHXvqigsOOwr4onUeNljegIC
        XC9h5exLFidQVB58MBjItMA81YVlZKBY9zth1neHeRTWlFTCx+WasvbS0HuYpF8+
        KPl7LJPjtI4XAAOLBntQGnPwCX2Ff/LgwqkZbOrHHkN444iLmViCXxNUDUMUR9bP
        A9/I5kwfyZ/mM5m8+IPhSXZ0f2uw1WLov1P4aeKkaaKCf5eL3n7/2vgq7kw2qSmR
        AGBZzW45PsjOEvygXFOy2n7AXL9nHogDiMdbe4aY2VT70sl0ccc4uvVOvVBMinOp
        d2rEpX0/8YE0dRXxukrM7i+r6lWy1lSKbP+0tQxQHNa/Cjg5W3uU+W9YmNUFc1w/
        7QT4SZrnRBEo++Xf9D3YNaOCFZXhy63IpY4eTQCJFQcXdnRbTXEdC3CtWNd7SV/h
        mfJYekb3GEV+10xLOvpe/+tCTeCDpFDJP6UuzLXBBADL2oV3D56hYlOlscjBokNU
        AYYlWgfwA91NjDsWW9mwapm/eLs4FNyH0JcMFTWH9dnl8B7PCUra/Lg/IVv6HkFE
        uCL7hVXGMbw2BZuCIC2VG1ZQ6QD64X8g5zL+HDsusQDbEJV2ZtojalTIjpxMksbR
        ZRsH+P3+NNOZOEwUdjJUAx8CAwEAAQ==
        -----END PUBLIC KEY-----'''
    cipher = PKCS1_v1_5.new(RSA.importKey(PUBLIC_KEY))
    # py3
    # cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd, encoding="utf8")))

    # py2
    cipher_text = base64.b64encode(cipher.encrypt(bytes(pwd)))
    return cipher_text.decode("utf-8")

class user():
    CSRF = "f3ae35f68d7e6e1551ad4420157b8f6c"
    Headers = {
        "Authorization": "Bearer", "loginToken": "", "AppVersion": "5.0.4",
        "User-Agent": "YiBan/5.0.4 Mozilla/5.0 (Linux; Android 5.1.1; SM-N960F Build/JLS36C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded", "Connection": "close",
        "Accept-Encoding": "gzip, deflate"
    }

    def __init__(self, mobile, password):
        self.mobile = mobile
        self.passwd = encryptPassword(password)
        self.session = requests.session()
        self.Cookies = {"csrf_token": self.CSRF}

    # 登陆模块
    def login(self):
        url = "https://m.yiban.cn:443/api/v4/passport/login"
        login_data = {"password": self.passwd,"mobile": self.mobile, "ct": "2", "identify": "355757884171113"}
        res = self.session.post(url, headers=self.Headers, data=login_data)
        return res.json()

    # 搜索校本化链接
    def select_xbh(self):
        url = "https://m.yiban.cn:443/api/v4/home"
        res = self.session.get(url, headers=self.Headers)
        return res.json()

    # 进入校本化，进行二次认证，获取verify_request、PHPSESSID、cpi三个值
    def access_xbh(self, url):
        res_1 = self.session.get(url, headers=self.Headers, allow_redirects=False)
        res_2 = self.session.get(res_1.headers['Location'], headers=self.Headers, allow_redirects=False)
        try:
            Location = res_2.headers['Location']
            self.verify_request = re.split("https://c.uyiban.com/#/\?verify_request=(.*)&", Location)[1]
            url = "https://api.uyiban.com:443/base/c/auth/yiban?verifyRequest={}&CSRF={}".format(self.verify_request, self.CSRF)
            self.Headers["Origin"] = "https://c.uyiban.com"
            res_3 = self.session.get(url, headers=self.Headers, cookies=self.Cookies)

            sess_id = re.search("PHPSESSID=(\w*);", res_3.headers['Set-Cookie']).group(0)
            self.Cookies["PHPSESSID"] = sess_id.split('=')[1].replace(";", "")
            cpi = re.search("cpi=((\w|%)*);", res_3.headers['Set-Cookie']).group(0)
            self.Cookies["cpi"] = cpi.split('=')[1].replace(";", "")

            return res_3.json()
        except:
            return False

    # 获取前一天打卡信息
    def yesterday_task(self):
        url_1 = "https://api.uyiban.com:443/officeTask/client/index/completedList?StartTime={}&EndTime={}&CSRF={}".format(T.yesterdayTime, T.EndTime, self.CSRF)
        res_1 = self.session.get(url_1, headers=self.Headers, cookies=self.Cookies)
        task = res_1.json()
        taskId = task['data'][0]['TaskId']

        url_2 = "https://api.uyiban.com:443/officeTask/client/index/detail?TaskId={}&CSRF={}".format(taskId, self.CSRF)
        res_2 = requests.get(url_2, headers=self.Headers, cookies=self.Cookies)
        res2_json = res_2.json()
        InitiateId = res2_json['data']['InitiateId']

        burp1_url = "https://api.uyiban.com:443/workFlow/c/work/show/view/{}?CSRF={}".format(InitiateId, self.CSRF)
        res_3 = requests.get(burp1_url, headers=self.Headers, cookies=self.Cookies)
        return res_3.json()

    # 寻找今日需要打卡的任务
    def select_today_task(self):
        url = "https://api.uyiban.com:443/officeTask/client/index/uncompletedList?StartTime={}&EndTime={}&CSRF={}".format(T.Starttime, T.EndTime, self.CSRF)
        res = requests.get(url, headers=self.Headers, cookies=self.Cookies)
        return res.json()

    # 打卡
    def today_task(self, TaskId):
        url = "https://api.uyiban.com:443/officeTask/client/index/detail?TaskId={}&CSRF={}".format(TaskId, self.CSRF)
        res = requests.get(url, headers=self.Headers, cookies=self.Cookies)
        res_json = res.json()

        Title = res_json['data']['Title']
        WFId = res_json['data']['WFId']

        message = self.yesterday_task()
        today = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        longitude = message['data']['Initiate']['FormDataJson'][0]['value']['longitude']
        latitude = message['data']['Initiate']['FormDataJson'][0]['value']['latitude']
        address = message['data']['Initiate']['FormDataJson'][0]['value']['address']
        temperature = message['data']['Initiate']['FormDataJson'][1]['value']
        status_1 = message['data']['Initiate']['FormDataJson'][2]['value'][0]
        status_2 = message['data']['Initiate']['FormDataJson'][3]['value'][0]
        contact = message['data']['Initiate']['FormDataJson'][4]['value'][0]
        accesshigh = message['data']['Initiate']['FormDataJson'][5]['value']
        stay = message['data']['Initiate']['FormDataJson'][6]['value']
        dormitory = message['data']['Initiate']['FormDataJson'][7]['value'][0]
        track = message['data']['Initiate']['FormDataJson'][8]['value']

        task_data = {
            'data':'{"a441d48886b2e011abb5685ea3ea4999":{"time":"%s","longitude":%s,"latitude":%s,"address":"%s"},"9cd65a003f4a2c30a4d949cad83eda0d":"%s","65ff68aeda65f345fef50b8b314184a7":["%s"],"b36100fc06308abbd5f50127d661f41e":["%s"],"c693ed0f20e629ab321514111f3ac2cb":["%s"],"91b48acca5f53c3221b01e5a1cf84f2f":"%s","9c96c042296de3e31a2821433cfec228":"%s","fd5e5be7f41a011f01336afc625d2fd4":["%s"],"c4b48d92f1a086996b0b2dd5f853c9f7":"%s"}' % (today, longitude, latitude, address, temperature, status_1, status_2, contact, accesshigh, stay, dormitory, track),
            'extend':u'{"TaskId":"%s","title":"任务信息","content":[{"label":"任务名称","value":"%s"},{"label":"发布机构","value":"学工部"}]}' % (TaskId, Title)
        }

        url_2 = "https://api.uyiban.com:443/workFlow/c/my/apply/{}?CSRF={}".format(WFId, self.CSRF)
        res_2 = requests.post(url_2, headers=self.Headers, cookies=self.Cookies, data=task_data)
        return res_2.json()

    def shouquan(self):
        url_1 = "https://openapi.yiban.cn:443/oauth/authorize?client_id=95626fa3080300ea&redirect_uri=https://f.yiban.cn/iapp7463&display=html"
        sq_headers = {"GET /oauth/authorize?client_id=95626fa3080300ea&redirect_uri=https": "/f.yiban.cn/iapp7463&display=html HTTP/1.1", "Connection": "close", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; SM-N960F Build/JLS36C; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 yiban_android/5.0.4", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3", "Referer": "https://c.uyiban.com/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7", "X-Requested-With": "com.yiban.app"}
        res = self.session.get(url_1, headers=sq_headers)
        url_2 = "https://oauth.yiban.cn:443/code/usersure"
        sq_data = {"client_id": "95626fa3080300ea", "redirect_uri": "https://f.yiban.cn/iapp7463", "state": '',
                      "scope": "1,2,3,", "display": "html"}
        res_2 = self.session.post(url_2, headers=sq_headers, data=sq_data)
        return res_2.json()