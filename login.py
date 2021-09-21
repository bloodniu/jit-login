# -*- coding:UTF-8 -*-
# Copyright (c) 2021 tx All rights reserved.
#   TX
import requests
import json
from bs4 import BeautifulSoup
import logging
import yaml

logging.getLogger().setLevel(logging.INFO)

with open('config.yaml', 'r',encoding='utf-8') as config:
    information = yaml.load(config.read(), Loader=yaml.FullLoader)
    username = information['username']
    password = information['password']

def login_jit(username, password):
    ss = requests.Session()
    url_1 = "http://authserver.jit.edu.cn/authserver/login"
    header_1 = {
        'Host': 'authserver.jit.edu.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://ehall.jit.edu.cn/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive'
    }
    form = {"username": username, 'password': password}
    re = ss.get(url_1)
    soup = BeautifulSoup(re.text, 'html.parser')
    attrs = soup.select('[class="login_area"] input[type="hidden"]')
    for k in attrs:
        if k.has_attr('name'):
            form[k['name']] = k['value']
        elif k.has_attr('id'):
            form[k['id']] = k['value']
    # 登录认证
    re = ss.post(url_1, data=form, headers=header_1, allow_redirects=False)
    a = re.status_code
    if a == 302:
        logging.info("\033[登录ing，准备信息填报]")
    re = ss.get('http://ehall.jit.edu.cn/login?service=http://ehall.jit.edu.cn/new/index.html')
    re = ss.get('http://ehall.jit.edu.cn/jsonp/userDesktopInfo.json')
    json_res = json.loads(re.text)
    try:
        name = json_res["userName"]
        print(name, "身份验证成功！")
    except Exception:
        print("认证失败！")
        return False

    return ss