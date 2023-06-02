# -*- coding: utf-8 -*-

import json
# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import logging
import random
import re
import socket

import pymongo
import requests
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from twisted.internet import defer
from twisted.internet.error import (
    ConnectError,
    ConnectionDone,
    ConnectionLost,
    ConnectionRefusedError,
    DNSLookupError,
    TCPTimedOutError,
    TimeoutError,
)
from twisted.web._newclient import ResponseFailed

from weibo.settings import MONGO_URI
from weibo.utils import dingtalk_util

logger = logging.getLogger(__name__)


def pare_cookie(cookies):
    cookies_dict = {}
    if cookies:
        for cookie in cookies.strip(" ").split(';'):
            key, str, value = cookie.partition('=')
            cookies_dict[key] = value
        return cookies_dict


class CookieMiddleware(object):
    """
    每次请求都随机从账号池中选择一个账号去访问
    """

    def __init__(self):
        client = pymongo.MongoClient(MONGO_URI)
        self.account_collection = client['weibo']['account']

    def process_request(self, request, spider):
        is_pc = request.url.find("weibo.com") != -1
        if is_pc:
            self.pc_cookie(request)
        else:
            self.m_cookie(request)

    def pc_cookie(self, request):
        all_count = self.account_collection.count_documents({'pc_status': 'success'})
        if all_count == 0:
            dingtalk_util.send_error('Current pc account pool is empty!! The spider will stop!!')
            raise Exception('Current pc account pool is empty!! The spider will stop!!')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'pc_status': 'success'})[random_index]
        logging.debug(f'Current account is {random_account.get("_id")}')
        # request.headers.setdefault('Cookie', random_account['pc_cookie'])
        cookies_dict = pare_cookie(random_account['pc_cookie'])
        request.cookies = cookies_dict
        request.meta['account'] = random_account

    def m_cookie(self, request):
        all_count = self.account_collection.count_documents({'m_status': 'success'})
        if all_count == 0:
            dingtalk_util.send_error('Current m account pool is empty!! The spider will stop!!')
            raise Exception('Current m account pool is empty!! The spider will stop!!')
        random_index = random.randint(0, all_count - 1)
        random_account = self.account_collection.find({'m_status': 'success'})[random_index]
        logging.debug(f'Current account is {random_account.get("_id")}')
        # request.headers.setdefault('Cookie', random_account['pc_cookie'])
        cookies_dict = pare_cookie(random_account['m_cookie'])
        request.cookies = cookies_dict
        request.meta['account'] = random_account


class RedirectMiddleware(object):
    """
    check account status
    HTTP Code = 302/418 -> cookie is expired or banned, and account status will change to 'error'
    """

    def __init__(self):
        client = pymongo.MongoClient(MONGO_URI)
        self.account_collection = client['weibo']['account']

    def getIp(self):
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        try:
            response_ip = requests.get("https://myip.ipip.net/", timeout=3)
            if response_ip.status_code == 200:
                response_ip.text
                return hostname + " " + ip + " " + response_ip.text
            else:
                return hostname + " " + ip
        except Exception as e:
            return hostname + " " + ip

    def process_response(self, request, response, spider):
        is_pc = request.url.find("weibo.com") != -1

        if is_pc:
            update_column = 'pc_status'
        else:
            update_column = 'm_status'
        http_code = response.status
        account = request.meta.get('account')
        if http_code == 302 or http_code == 403:
            # title = f'亲爱的@{account.get("_id")}，您预留的cookie出错了，请及时更新'
            # content = f'### cookie出错了，请及时更新@{account.get("_id")} \n' \
            #           f'### 错误的链接 ： {request.url} \n' \
            #           f'# [请点击此链接更新cookie](http://mgt.beyonca-qa.com/magnet?type=update&_id={account.get("_id")}&name={account.get("name")})'
            # atMobiles = [account.get("_id")]
            # dingtalk_util.send_markdown_cookie(title, content, atMobiles)
            #
            # self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
            #                                             {'$set': {update_column: 'error'}})
            logger.error(
                f"Current account {account.get('_id')},{account.get('name')} is error {request.url} {response.text}")
            return request
        elif http_code == 418 or http_code == 414:
            ip_address = self.getIp()
            proxy = request.meta.get('proxy')
            if not proxy:
                msg = f'IP at {ip_address}is invalid, will stop the programme! {request.url}'
                dingtalk_util.send_error(msg)
                spider.logger.error(msg)
                raise Exception(msg)
            else:
                spider.logger.error(
                    f'IP at {proxy}is invalid, please change the ip proxy or stop the programme! {request.url}')
            return request

        else:
            try:
                result = json.loads(response.text)
                if result.get('ok') == -100:
                    logger.error(
                        f'Current account is error,请及时更新账号 {account.get("_id")},{account.get("name")} at {request.url} ')

                    title = f'亲爱的@{account.get("_id")}，您预留的cookie出错了，请及时更新'
                    content = f'### cookie出错了，请及时更新@{account.get("_id")} \n' \
                              f'### 错误的链接 ： {request.url} \n' \
                              f'# [请点击此链接更新cookie](http://mgt.beyonca-qa.com/magnet?type=update&_id={account.get("_id")}&name={account.get("name")})'
                    atMobiles = [account.get("_id")]
                    dingtalk_util.send_markdown_cookie(title, content, atMobiles)

                    self.account_collection.find_one_and_update({'_id': request.meta['account']['_id']},
                                                                {'$set': {update_column: 'error'}})
                    return request
            except json.decoder.JSONDecodeError:
                logger.error(
                    f'Json decode error,{request.meta.get("proxy")} {request.meta.get("account").get("_id")}  {response.text}')
                return request
            return response


class CSRFTokenMiddleware(object):

    def process_request(self, request, spider):
        pass


class RetryCommentMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        try:
            result = json.loads(response.text)
            if not result.get('ok') == 1:
                retry_times = request.meta.get('retry_times', 0)
                url = request.url
                logger.info(f'Retrying times retry_times:{retry_times} {url} {result}')
                return self._retry(request, 'Status not OK', spider) or response
            return response
        except json.decoder.JSONDecodeError:
            logger.info('Json decode error, content %s', response.text)
            return self._retry(request, 'Json Decode Error', spider) or response


class ProxypoolMiddleware(object):
    """
    proxy middleware for changing proxy
    """

    def __init__(self, proxypool_url):
        self.logger = logging.getLogger(__name__)
        if re.search('^https?://\S+:\S+@\S+', proxypool_url):
            result = re.search('https?://(\S+):(\S+)@\S+', proxypool_url)
            self.auth = result.group(1), result.group(2)
            self.proxypool_url = re.sub('(https?://)\S+:\S+@(\S+)', r'\1\2', proxypool_url)
        else:
            self.auth = None
            self.proxypool_url = proxypool_url

    def get_random_proxy(self):
        """
        get random proxy form proxypol
        :return:
        """
        try:
            if getattr(self, 'auth') and self.auth:
                response = requests.get(self.proxypool_url, timeout=5, auth=self.auth)
            else:
                response = requests.get(self.proxypool_url, timeout=5)
            if response.status_code == 200:
                proxy = response.text
                return proxy
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        """
        if retry_times > 0，get random proxy
        :param request:
        :param spider:
        :return:
        """
        # if request.meta.get('retry_times'):
        proxy = self.get_random_proxy()
        # proxy = "127.0.0.1:7890"
        # self.logger.debug('Get proxy %s', proxy)
        if proxy:
            uri = 'http://{proxy}'.format(proxy=proxy)
            self.logger.debug('Using proxy %s', proxy)
            request.meta['proxy'] = uri

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            proxypool_url=settings.get('PROXYPOOL_URL')
        )


class ProxyDecreaseMiddleware(object):
    # IOError is raised by the HttpCompression middleware when trying to
    # decompress an empty response
    EXCEPTIONS_TO_RETRY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                           ConnectionRefusedError, ConnectionDone, ConnectError,
                           ConnectionLost, TCPTimedOutError, ResponseFailed,
                           IOError, TunnelError)

    def __init__(self, settings):
        self.proxy_decrease_url = settings.get('PROXY_DECREASE_URL')
        self.proxy_max_url = settings.get('PROXY_MAX_URL')
        self.proxy_decrease_http_codes = set(int(x) for x in settings.getlist('PROXY_DECREASE_HTTP_CODES'))
        self.proxy_max_http_codes = set(int(x) for x in settings.getlist('PROXY_MAX_HTTP_CODES'))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):

        if response.status in self.proxy_max_http_codes:
            self.proxy_max(request)
            return response
        elif response.status in self.proxy_decrease_http_codes:
            self.proxy_decrease(request)
            return response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY):
            self.proxy_decrease(request)

    def proxy_decrease(self, request):
        try:
            proxy = request.meta.get('proxy')
            if proxy:
                proxy = proxy.replace('http://', '')
                url = self.proxy_decrease_url.format(proxy=proxy)
                response = requests.get(url)
                if response.status_code == 200:
                    logger.debug('Proxy decrease success')
                else:
                    logger.debug('Proxy decrease failed')
        except requests.ConnectionError:
            logger.error('Proxy decrease failed')

    def proxy_max(self, request):
        try:
            proxy = request.meta.get('proxy')
            if proxy:
                proxy = proxy.replace('http://', '')
                url = self.proxy_max_url.format(proxy=proxy)
                response = requests.get(url)
                if response.status_code == 200:
                    logger.debug('Proxy decrease success')
                else:
                    logger.debug('Proxy decrease failed')
        except requests.ConnectionError:
            logger.error('Proxy max failed')
