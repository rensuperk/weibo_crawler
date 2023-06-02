# import json
# import re
#
# import scrapy
# from environs import Env
# from scrapy_redis.spiders import RedisSpider
#
# from weibo.items import *
#
# env = Env()
#
#
# class MUserAttentionRedisSpider(RedisSpider):
#     """
#     comment spider of single weibo
#     """
#     name = 'm_user_attention_redis'
#     allowed_domains = ['m.weibo.cn']
#     start_url = 'm_user_attention_redis:start_urls'
#     next_url = 'https://m.weibo.cn/api/attentionvist/tagUsersCounts?to_uid={uid}'
#     custom_settings = {
#         # 'DOWNLOAD_DELAY': 10,
#         # 'COOKIES_ENABLED': True,
#         # 'LOG_LEVEL': 'DEBUG',
#         # 'COOKIES_DEBUG': True,
#         # # 'SCHEDULER': 'scrapy.core.scheduler.Scheduler',
#         # # 'REDIS_START_URLS_BATCH_SIZE': 5,
#         # 'RETRY_TIMES': 5,
#         # # 去重持久化
#         # 'SCHEDULER_PERSIST': True,
#         # # 重新爬取
#         # 'SCHEDULER_FLUSH_ON_START': False,
#         # 'DOWNLOADER_MIDDLEWARES': {
#         #     'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
#         #     'weibo.middlewares.CookieMiddleware': 100,
#         #     'weibo.middlewares.RedirectMiddleware': 200,
#         #     # 'weibo.middlewares.ProxypoolMiddleware': 555 if env.bool('PROXYPOOL_ENABLED', True) else None,
#         # },
#         # 'ITEM_PIPELINES': {
#         # 'weibo.pipelines.CommentPipeline': 300,
#         # 'weibo.pipelines.TimePipeline': 400,
#         # 'weibo.pipelines.MongoPipeline': 500,
#         # }
#     }
#
#     def parse(self, response):
#
#         """
#        parse comments
#        :param response:
#        :return:
#        """
#         result = json.loads(response.text)
#         if result.get('ok') == 1 and result.get('data') and result.get('data').get('tag_users'):
#             tag_users = result.get('data').get('tag_users')
#             uid = re.findall('uid=(\d*)', response.url)[0]
#             self.logger.info(f'成功下载 {response.url}')
#
#             first_row = True
#             for tag_user in tag_users:
#                 user_attention_item = UserAttentionItem()
#                 tag_user['user_id'] = uid
#                 user_attention_item['data'] = tag_user
#                 if first_row:
#                     user_attention_item['first_row'] = True
#                     first_row = False
#                 self.logger.debug(
#                     f'user_detail {tag_user.get("user_id")} {tag_user.get("tag_id")} {tag_user.get("tag_name")}')
#                 yield user_attention_item
#         else:
#             self.logger.error(f'Result not ok {response.url} {result}')
#
#     # 新版本没有这个方法所以需要重写下
#     def make_requests_from_url(self, url):
#         return scrapy.Request(url, dont_filter=True)
