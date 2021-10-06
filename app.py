#-*- coding:utf-8 -*-
from flask import Flask
from flask import request, render_template
import pymysql
from config import user

app = Flask(__name__)
db = pymysql.connect(host='localhost', user='atao', password='atao', database='yiban')

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/addstudent', methods=['POST'])
def addstudent():
    try:
        mobile = request.form.get("mobile")
        password = request.form.get("password")
    except:
        return render_template("add_success.html", text="缺少参数!请重新输入")
    if len(mobile) != 11:
        return render_template("add_success.html", text="亲!您的手机号输入有误")
    if "'" in mobile or "'" in password:
        return render_template("add_success.html", text="don't hack me!")

    sql = 'SELECT * FROM MJUstudents where mobile = "'+mobile+'"'
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

    if len(results) == 0:
        student = user(mobile, password)
        login = student.login()
        if login['response'] != 100:
            return render_template("add_success.html", text="用户名或密码错误")
        try:
            name = login['data']['user']['name']
            print(name)
            sql_1 = 'INSERT INTO MJUstudents (name, mobile, password ) VALUES ( "{}", "{}", "{}")'.format(name, mobile, password)
            try:
                cursor1 = db.cursor()
                cursor1.execute(sql_1)
                db.commit()
            except:
                db.rollback()
                return render_template("add_success.html", text="程序出错!请稍后尝试")
        except:
            return render_template("add_success.html", text="程序出错!请稍后尝试")
    else:
        return render_template("add_success.html", text="手机号已经添加过")
    return render_template("add_success.html", text="添加成功!")

@app.route('/deletestudent', methods=['POST'])
def deletestudent():
    try:
        mobile = request.form.get("mobile")
    except:
        return render_template("add_success.html", text="缺少参数!请重新输入")
    if len(mobile) != 11:
        return render_template("add_success.html", text="亲!您的手机号输入有误")
    sql = "SELECT * FROM MJUstudents where mobile = '{}'".format(mobile)
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()

    if len(results) == 1:
        sql_1 = "DELETE FROM MJUstudents where mobile = '{}'".format(mobile)
        try:
            cursor1 = db.cursor()
            cursor1.execute(sql_1)
            db.commit()
        except:
            db.rollback()
            return render_template("add_success.html", text="程序出错!请稍后尝试")
    elif len(results) == 0:
        return render_template("add_success.html", text="手机号不存在数据库中")
    return render_template("add_success.html", text="删除成功!")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
    app.run(debug=False)
