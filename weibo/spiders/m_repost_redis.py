import json
import re

import scrapy
from environs import Env
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from weibo.items import *

env = Env()


class MRepostRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_repost_redis'
    allowed_domains = ['m.weibo.cn']
    start_url = RepostItem.start_url
    next_url = RepostItem.url
    custom_settings = {
        # 'DOWNLOAD_DELAY': 10,
        # 'COOKIES_ENABLED': True,
        # 'LOG_LEVEL': 'DEBUG',
        # 'COOKIES_DEBUG': True,
        # # 'SCHEDULER': 'scrapy.core.scheduler.Scheduler',
        # # 'REDIS_START_URLS_BATCH_SIZE': 5,
        # 'RETRY_TIMES': 5,
        # # 去重持久化
        # 'SCHEDULER_PERSIST': True,
        # # 重新爬取
        # 'SCHEDULER_FLUSH_ON_START': False,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'weibo.middlewares.CookieMiddleware': 100,
        #     'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
        #     'weibo.middlewares.RedirectMiddleware': 200,
        #     # 'weibo.middlewares.ProxypoolMiddleware': 555 if env.bool('PROXYPOOL_ENABLED', True) else None,
        # }
    }

    def parse(self, response):
        """
        parse comments
        :param response:
        :return:
        """
        # cur_page = response.meta['cur_page']
        # self.logger.info('Crawled Page %s', cur_page)

        result = json.loads(response.text)
        if result.get('ok') == 1:
            data = result.get('data', {})
            reposts = data.get('data')
            weibo_id = re.findall('id=(\d*)', response.url)[0]
            if reposts:
                self.logger.info(f'成功下载 {response.url}')
                first_row = True
                for repost in reposts:
                    repost_item = RepostItem()
                    repost['user_id'] = repost.get('user').get('id')
                    repost['weibo'] = weibo_id
                    repost_item['data'] = repost
                    if first_row:
                        repost_item['first_row'] = True
                        first_row = False
                    self.logger.debug('Comment %s %s %s', repost['id'], repost['text'], repost['created_at'])
                    yield repost_item

                page = re.findall('page=(\d*)', response.url)[0]
                url = self.next_url.format(id=weibo_id, page=int(page) + 1)
                self.logger.info(f"repost next_url {url}")
                yield Request(url, self.parse, meta=response.meta)
            else:
                self.logger.error('No Repost Data %s', data)
        else:
            self.logger.error('Result not ok %s', result)

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)
