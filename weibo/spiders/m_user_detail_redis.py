import json
import re

import scrapy
from scrapy_redis.spiders import RedisSpider

from weibo.items import *
from weibo.utils.redis_utils import RedisClient



class MUserDetailRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_user_detail_redis'
    allowed_domains = ['weibo.com']
    start_url = 'm_user_detail_redis:start_urls'
    next_url = 'https://weibo.com/ajax/profile/detail?uid={user_id}'
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

        """
       parse comments
       :param response:
       :return:
       """
        result = json.loads(response.text)
        uid = re.findall('uid=(\d*)', response.url)[0]
        if result.get('ok') == 1 and result.get('data'):
            self.logger.info(f'成功下载 {response.url}')
            user_detail_result = result.get('data', {})
            user_detail_item = UserDetailItem()
            user_detail_result['id'] = uid
            user_detail_item['data'] = user_detail_result
            self.logger.debug(f'user_detail {user_detail_result.get("id")} {user_detail_result.get("created_at")}')
            yield user_detail_item
        else:
            if result.get("msg") == "该用户不存在(20003)":
                RedisClient().db.sadd("not_exist_user_id",uid)
            self.logger.error('Result not ok %s', result)

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)