import json
import re

import scrapy
from environs import Env
from scrapy_redis.spiders import RedisSpider

from weibo.items import *

env = Env()


class MUserAttentionMemberRedisSpider(RedisSpider):
    """
    comment spider of single weibo
    """
    name = 'm_user_attention_member_redis'
    allowed_domains = ['m.weibo.cn']
    start_url = UserAttentionMemberItem.start_url

    def parse(self, response):

        """
       parse comments
       :param response:
       :return:
       """
        result = json.loads(response.text)
        if result.get('ok') == 1 and result.get('data') and result.get('data').get('member_users'):
            member_users = result.get('data').get('member_users')
            uid = re.findall('to_uid=(\d*)', response.url)[0]
            tag_id = result.get('data').get('tag_id')
            self.logger.info(f'成功下载 {response.url}')
            first_row = True
            for member_user in member_users:
                user_attention_member_item = UserAttentionMemberItem()
                member_user['user_id'] = uid
                member_user['tag_id'] = tag_id
                member_user['tag_name'] = result.get('data').get('tag_name')
                user_attention_member_item['data'] = member_user
                self.logger.debug(
                    f'user_detail {member_user.get("id")} {member_user.get("user_id")} {member_user.get("tag_id")} {member_user.get("tag_name")}')
                if first_row:
                    user_attention_member_item['first_row'] = True
                    first_row = False
                yield user_attention_member_item
        else:
            self.logger.error(f'Result not ok {response.url} {result}')

    # 新版本没有这个方法所以需要重写下
    def make_requests_from_url(self, url):
        return scrapy.Request(url, dont_filter=True)
