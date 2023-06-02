#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2019-12-07 21:27
"""
import scrapy.core.scraper
import scrapy.utils.misc

from weibo.spiders.m_weibo_redis import MWeiboRedisSpider


def warn_on_generator_with_return_value_stub(spider, callable):
    pass


scrapy.utils.misc.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub
scrapy.core.scraper.warn_on_generator_with_return_value = warn_on_generator_with_return_value_stub

import os
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders.m_attitude_redis import MAttitudeRedisSpider
from spiders.m_comment_redis import MCommentRedisSpider
from spiders.m_repost_redis import MRepostRedisSpider
from spiders.m_user_weibo_redis import MUserWeiboRedisSpider
from spiders.m_user_attention_members_redis import MUserAttentionMemberRedisSpider
from spiders.m_user_attention_tag_redis import MUserAttentionTagRedisSpider
from spiders.m_user_detail_redis import MUserDetailRedisSpider

if __name__ == '__main__':
    mode = sys.argv[1]
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ['SCRAPY_SETTINGS_MODULE'] = f'settings'
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    mode_to_spider = {
        'weibo': MWeiboRedisSpider,
        'comment': MCommentRedisSpider,
        'repost': MRepostRedisSpider,
        'attitude': MAttitudeRedisSpider,
        'user_detail': MUserDetailRedisSpider,
        'user_attention_tag': MUserAttentionTagRedisSpider,
        'user_attention_member': MUserAttentionMemberRedisSpider,
        'user_weibo': MUserWeiboRedisSpider,
    }
    process.crawl(mode_to_spider[mode])
    # the script will block here until the crawling is finished
    process.start()
