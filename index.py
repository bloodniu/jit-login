# -*- coding:UTF-8 -*-
# Copyright (c) 2021 tx All rights reserved.
#   TX

import datetime
import requests
import json
import yaml
import time
from bs4 import BeautifulSoup
from login import login_jit
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header


with open('config.yaml', 'r',encoding='utf-8') as config:
    information = yaml.load(config.read(), Loader=yaml.FullLoader)
    username = information['username']
    password = information['password']
    email = information['email']

isDebug = False

jinri = time.strftime( "%Y%m%d", time.localtime())

ss = requests.Session()

def get_report_data(ss):
    ss.get("http://ehallapp.jit.edu.cn/emapflow/sys/lwReportEpidemic/index.do?amp_sec_version_=1&gid_=NERHZGVZTkJJNFZKQThVQlcrSTNEUkVUcW5QQVBwekt5MllCN1E3bDlMMGs2bEEvVW55YmtCbHpNYjJIa2wwUWkxbkYvc1ZPcmlKUWxDVUYyQlc5Smc9PQ&EMAP_LANG=zh&THEME=millennium#/newdailyReport")
    latest_url = "http://ehallapp.jit.edu.cn/emapflow/sys/lwReportEpidemic/modules/newdailyReport/getLatestnewDailyReportData.do"
    wid_url = "http://ehallapp.jit.edu.cn/emapflow/sys/lwReportEpidemic/modules/newdailyReport/getMyTodayReportWid.do"
    userinfo_url = "http://ehallapp.jit.edu.cn/emapflow/sys/lwReportEpidemic/api/base/getUserDetailDB.do"
    last_res = ss.post(latest_url)
    wid_res = ss.post(wid_url)
    userinfo_res = ss.post(userinfo_url)
    try:
        tempFormData = {}
        userInfo = json.loads(userinfo_res.text)['data']
        try:
            wid_data = json.loads(wid_res.text)['datas']['getMyTodayReportWid']['rows'][0]
            tempFormData.update(wid_data)
        except Exception:
            print('【getMyTodayReportWid FAILED】')
        try:
            last_report = json.loads(last_res.text)['datas']['getLatestnewDailyReportData']['rows'][0]
            tempFormData.update(last_report)
        except Exception:
            print('getLatestnewDailyReportData FAILED】')
            raise
        tempFormData['USER_ID'] = username
        tempFormData['IDCARD_NO'] = userInfo['IDENTITY_CREDENTIALS_NO']
        tempFormData['GENDER_CODE'] = userInfo['GENDER_CODE']
        tempFormData['USER_NAME'] = userInfo['USER_NAME']
        tempFormData['DEPT_CODE'] = userInfo['DEPT_CODE']
        tempFormData['DEPT_NAME'] = userInfo['DEPT_NAME']
        if isDebug:
            print(tempFormData)
    except Exception as e:
        print(e)
        print("【获取填报信息失败，请手动填报】")
        exit()
    return tempFormData


def load_params(ss):
    json_form = get_report_data(ss)
    params = {
        "CZRQ": "%Y-%m-%d %H:%M:%S",
        "CREATED_AT": "%Y-%m-%d %H:%M:%S",
        "NEED_CHECKIN_DATE": "%Y-%m-%d"
    }
    today = datetime.datetime.now()
    today_list = ['CZRQ', 'CREATED_AT', 'NEED_CHECKIN_DATE']
    for key in params.keys():
        if key in today_list:
            params[key] = today.strftime(params[key])
        json_form[key] = params[key]
    return json_form

if __name__ == '__main__':
    ss = login_jit(username,password)
    tb = get_report_data(ss)
    ss.get(
        "http://ehallapp.jit.edu.cn/emapflow/sys/lwReportEpidemic/index.do?amp_sec_version_=1&gid_=NERHZGVZTkJJNFZKQThVQlcrSTNEUkVUcW5QQVBwekt5MllCN1E3bDlMMGs2bEEvVW55YmtCbHpNYjJIa2wwUWkxbkYvc1ZPcmlKUWxDVUYyQlc5Smc9PQ&EMAP_LANG=zh&THEME=millennium#/newdailyReport")
    url = 'http://ehallapp.jit.edu.cn/emapflow/sys/lwReportEpidemic/modules/newdailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do'
    json_form = load_params(ss)
    res = ss.post(url, data=json_form)
    try:
        if json.loads(res.text)['datas']['T_REPORT_EPIDEMIC_CHECKIN_SAVE'] == 1:
            print("填报成功！")
        else:
            print("填报失败！")
    except Exception:
        soup = BeautifulSoup(res.text, "html.parser")
        tag = soup.select('.underscore.bh-mt-16')
        if len(tag) > 1:
            print(tag[0].text.replace('\n', ''))
        else:
            print(res.text)
        print("填报失败！")
    # 邮件通知系统
    email_from = ""
    email_to = email
    hostname = "smtp.qq.com"
    login = ""
    password = ""
    subject = jinri+ '健康填报通知'
    text = (jinri + str(res.text))

    smtp = SMTP_SSL(hostname)
    smtp.login(login, password)

    msg = MIMEText(text, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["from"] = email_from
    msg["to"] = email_to

    smtp.sendmail(email_from, email_to, msg.as_string())
    smtp.quit()
    print("健康填报邮件通知已发送")
