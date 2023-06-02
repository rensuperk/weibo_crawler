#!/usr/bin/env python
# encoding: utf-8
import base64
import hashlib
import hmac
import time
import urllib.parse

import requests

from weibo.settings import DINGTALK_TOKEN, DINGTALK_SECRET, COOKIE_DINGTALK_SECRET, COOKIE_DINGTALK_TOKEN


def _sign(timestamp, secret):
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign


def get_url():
    timestamp = str(round(time.time() * 1000))
    sign = _sign(timestamp, DINGTALK_SECRET)
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_TOKEN}&timestamp={timestamp}&sign={sign}'
    return url


def get_cookie_url():
    timestamp = str(round(time.time() * 1000))
    sign = _sign(timestamp, COOKIE_DINGTALK_SECRET)
    url = f'https://oapi.dingtalk.com/robot/send?access_token={COOKIE_DINGTALK_TOKEN}&timestamp={timestamp}&sign={sign}'
    return url


def send_error(msg):
    timestamp = str(round(time.time() * 1000))
    sign = _sign(timestamp, DINGTALK_SECRET)
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_TOKEN}&timestamp={timestamp}&sign={sign}'
    response = requests.post(
        url=url,
        headers={"Content-Type": "application/json"},
        json={
            "msgtype": "text",
            "text": {
                "content": f"{msg}"
            },
            "at": {
                "isAtAll": "false"
            }
        })


def send_markdown_cookie(title, text, atMobile):
    url = get_url()
    response = requests.post(
        url=url,
        headers={"Content-Type": "application/json"},
        json={
            "msgtype": "markdown",
            "markdown": {
                "title": title,
                "text": text
            },
            "at": {
                "atMobiles": atMobile,
                "isAtAll": "false"
            }
        })


if __name__ == '__main__':
    account = {"_id": "17610477667", "name": "任凯"}
    title = f'TEST cookie出错了，请及时更新@{account.get("_id")}'
    content = f'### TEST cookie出错了，请及时更新@{account.get("_id")} \n' \
              f'### 错误的链接 ： 这是测试链接 \n' \
              f'# [请点击此连接更新cookie](http://mgt.beyonca-qa.com/magnet?type=update&_id={account.get("_id")}&name={account.get("name")})'
    atMobiles = [account.get("_id")]
    send_markdown_cookie(title, content, atMobiles)
