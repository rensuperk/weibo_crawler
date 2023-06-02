import datetime as datetime
import json
import logging
import re

import scrapy
from environs import Env
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from weibo.items import *

env = Env()


class MUserWeiboRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_user_weibo_redis'
    allowed_domains = ['m.weibo.cn']
    start_url = UserWeiboItem.start_url
    next_url = UserWeiboItem.url
    since_data = '2019-07-22'
    max_user_weibo_page = 120
    custom_settings = {
        "SCHEDULER": 'weibo.utils.bloomfilter.scheduler.Scheduler',
        "DUPEFILTER_CLASS": 'weibo.utils.bloomfilter.dupefilter.RFPDupeFilter',
    }

    def compare_time(self, time_str):
        since = datetime.datetime.strptime(self.since_data, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        created_at = datetime.datetime.strptime(time_str, '%a %b %d %H:%M:%S %z %Y')
        return created_at >= since

    def parse(self, response):

        """
               parse comments
               :param response:
               :return:
               """
        # cur_page = response.meta['cur_page']
        # self.logger.info('Crawled Page %s', cur_page)
        result = json.loads(response.text)
        if result.get('ok') == 1 and result.get('data').get('cards'):
            data = result.get('data', {})
            # cardlistInfo = data.get('cardlistInfo', {})
            cards = data.get('cards', [])
            uid = re.findall('uid=(\d*)', response.url)[0]
            page = re.findall('page=(\d*)', response.url)[0]
            start = False
            self.logger.info(f'成功下载 {response.url}')
            first_row = True
            for card in cards:
                weibo = card.get('mblog')
                if card.get('card_type') == 9 and weibo:
                    weibo_item = UserWeiboItem()
                    # 比较时间 大于等于since_date就继续爬取
                    start = self.compare_time(weibo.get('created_at'))
                    if start:
                        weibo['user_id'] = uid
                        weibo_item['data'] = weibo
                        if int(page) >= self.max_user_weibo_page:
                            weibo_item['data']['user']['last_page'] = page
                        if first_row:
                            weibo_item['first_row'] = True
                            first_row = False
                        self.logger.debug('weibo %s %s %s', weibo.get('id'), weibo.get('text'), weibo.get('created_at'))
                        yield weibo_item

            if start and int(page) < self.max_user_weibo_page:
                url = self.next_url.format(uid=uid, page=int(page) + 1)
                logging.info(f'{self.name} add url {url}')
                yield Request(url, self.parse, meta=response.meta, dont_filter=False)
                url = self.next_url.format(uid=uid, page=int(page) + 2)
                logging.info(f'{self.name} add url {url}')
                yield Request(url, self.parse, meta=response.meta, dont_filter=False)
                url = self.next_url.format(uid=uid, page=int(page) + 3)
                logging.info(f'{self.name} add url {url}')
                yield Request(url, self.parse, meta=response.meta, dont_filter=False)
        else:
            self.logger.error('Result not ok %s', result)

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)
