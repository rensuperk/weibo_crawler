import json
import re

import scrapy
from environs import Env
from scrapy import Request
from scrapy_redis.spiders import RedisSpider

from weibo.items import CommentNewItem

env = Env()


class MCommentRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_comment_redis'
    allowed_domains = ['m.weibo.cn']
    start_url = CommentNewItem.start_url
    next_url = CommentNewItem.url

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
        #     'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
        #     'weibo.middlewares.CookieMiddleware': 100,
        #     'weibo.middlewares.RedirectMiddleware': 200,
        #     # 'weibo.middlewares.ProxypoolMiddleware': 555 if env.bool('PROXYPOOL_ENABLED', True) else None,
        # },
        # 'ITEM_PIPELINES': {
        # 'weibo.pipelines.CommentPipeline': 300,
        # 'weibo.pipelines.TimePipeline': 400,
        # 'weibo.pipelines.MongoPipeline': 500,
        # }
    }

    def parse(self, response):
        # """
        #         parse weibos
        #         :param response: weibos response
        #         """
        result = json.loads(response.text)
        if result.get('ok') == 1:
            data = result.get('data', {})
            comments = data.get('data')
            max_id = data.get('max_id')
            weibo_id = re.findall('id=(\d*)', response.url)[0]
            if max_id:
                url = self.next_url.format(id=weibo_id, max_id=max_id)
                self.logger.info('next_url: {}'.format(url))
                yield Request(url, self.parse, meta=response.meta, dont_filter=False)
            if comments:
                self.logger.info(f'成功下载 {response.url}')
                first_row = True
                for comment in comments:
                    comment_item = CommentNewItem()
                    comment['weibo'] = weibo_id
                    comment['user_id'] = comment.get('user').get('id')
                    comment_item['data'] = comment
                    if first_row:
                        comment_item['first_row'] = True
                        first_row = False
                    self.logger.debug('Comment %s %s %s', comment.get('id')
                                      , comment.get('text'), comment.get('created_at'))
                    yield comment_item
            else:
                self.logger.error('No Comments Data %s', data)
        else:
            self.logger.error('Result not ok %s', result)

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)
