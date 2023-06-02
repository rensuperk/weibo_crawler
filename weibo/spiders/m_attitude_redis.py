import json
import re

import scrapy
from environs import Env
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from weibo.items import *

env = Env()


class MAttitudeRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_attitude_redis'
    allowed_domains = ['m.weibo.cn']
    start_url = AttitudeItem.start_url
    next_url = AttitudeItem.url

    def parse(self, response):

        """
               parse comments
               :param response:
               :return:
               """
        result = json.loads(response.text)
        if result.get('ok') == 1 and result.get('data').get('data'):
            data = result.get('data', {})
            # cardlistInfo = data.get('cardlistInfo', {})
            attitudes = data.get('data', [])
            weibo_id = re.findall('id=(\d*)', response.url)[0]
            page = re.findall('page=(\d*)', response.url)[0]
            self.logger.info(f'成功下载 {response.url}')
            first_row = True
            for attitude in attitudes:
                user = attitude.get('user')
                attitude_item = AttitudeItem()
                attitude['weibo'] = weibo_id
                attitude['user_id'] = user.get('id')
                attitude_item['data'] = attitude
                if first_row:
                    attitude_item['first_row'] = True
                    first_row = False
                self.logger.debug('weibo %s %s %s', attitude.get('id'), attitude.get('weibo'),
                                  attitude.get('created_at'))
                yield attitude_item

            url = self.next_url.format(weibo_id=weibo_id, page=int(page) + 1)
            self.logger.info(f'attitude next_url {url}')
            yield Request(url, self.parse, meta=response.meta, dont_filter=False)
        else:
            self.logger.error('Result not ok %s', result)

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)
