#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/15
"""
import sys

import redis

from settings import INIT_USERS
from weibo.items import WeiboItem
from weibo.settings import REDIS_URL
from weibo.utils import redis_utils
from weibo.utils.redis_utils import RedisClient

redis_client = redis.Redis.from_url(REDIS_URL)


def redis_init(start_url, urls):
    r = RedisClient().db
    print(f'Add urls to {start_url}')
    for url in urls:
        r.sadd(start_url, url)


def init_m_weibo_redis_spider():
    redis_utils.bak_weibo_filter()
    urls = []
    for init_weibo in INIT_USERS:
        urls.append(WeiboItem.url.format(uid=init_weibo, page=1))
    # urls.append(WeiboItem.url.format(uid="5675889356", page=1))
    redis_init(WeiboItem.start_url, urls)


if __name__ == '__main__':
    mode = sys.argv[1]
    mode_to_fun = {
        # 'user_detail': init_m_user_detail_redis_spider,
        # 'user_attention_tag': init_m_user_attention_tag_redis_spider,
        # 'user_attention_member': init_m_user_attention_member_redis_spider,
        # 'comment': init_m_comment_redis_spider,
        # 'repost': init_m_repost_redis_spider,
        'weibo': init_m_weibo_redis_spider,
        # 'user_weibo': init_m_user_weibo_redis_spider,
        # 'attitude': init_m_attitude_redis_spider,
    }
    mode_to_fun[mode]()
