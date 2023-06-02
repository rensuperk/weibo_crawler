import json
import re

import scrapy
from environs import Env
from scrapy_redis.spiders import RedisSpider

from weibo.items import *

env = Env()


class MUserAttentionTagRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_user_attention_tag_redis'
    allowed_domains = ['m.weibo.cn']
    start_url = UserAttentionTagItem.start_url
    next_url = UserAttentionTagItem.url

    def parse(self, response):

        """
       parse comments
       :param response:
       :return:
       """
        result = json.loads(response.text)
        if result.get('ok') == 1 and result.get('data') and result.get('data').get('relations_tags'):
            self.logger.info(f'成功下载 {response.url}')
            user_id = re.findall('uid=(\d*)', response.url)[0]
            user = result.get('data').get('user')
            relations_tags = result.get('data').get('relations_tags')
            user_attention_tag_item = UserAttentionTagItem()
            user_attention_tag_item["data"] = relations_tags
            user_attention_tag_item["data"]["user"] = user
            user_attention_tag_item["data"]["user_id"] = user_id
            self.logger.debug(f"user_attention_tag {user_id}")
            yield user_attention_tag_item
        else:
            self.logger.error(f'Result not ok {response.url} {result}')

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)
