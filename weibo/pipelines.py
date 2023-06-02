# -*- coding: utf-8 -*-
import logging
import re
import time
from datetime import datetime

import dateparser
import pymongo
import pytz
from redis.client import Redis
from twisted.internet.threads import deferToThread

from weibo.items import *
from weibo.utils.bloomfilter.bloomfilter import BloomFilter

logging.getLogger('scrapy.core.scraper').setLevel(logging.INFO)


class TimePipeline():

    def process_item(self, item, spider):
        """
        add crawled_at attr
        :param item:
        :param spider:
        :return:
        """
        data = item.get('data')
        if data:
            user = data.get('user')
            if user:
                user['crawled_at'] = datetime.now(tz=pytz.utc)
            data['crawled_at'] = datetime.now(tz=pytz.utc)
        return item


class RecentTimePipeline():
    """
    weibo pipeline
    """

    def parse_time(self, date):
        """
        parse weibo time
        :param date:
        :return:
        """
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date + ':00'
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00:00'
        return dateparser.parse(date)

    def process_item(self, item, spider):
        """
        process weibo item
        :param item:
        :param spider:
        :return:
        """
        if isinstance(item, AttitudeItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))
        return item


class MongoPipeline(object):
    """
    mongodb pipeline
    """

    def __init__(self, mongo_uri, mongo_db):
        """
        init conn
        :param mongo_uri:
        :param mongo_db:
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        """
        get settings
        :param crawler:
        :return:
        """
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
        )

    def open_spider(self, spider):
        """
        create conn while creating spider
        :param spider:
        :return:
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[UserItem.collection].create_index([('id', pymongo.ASCENDING)], unique=True)
        self.db[UserItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[UserWeiboItem.collection + "_" + time.strftime('%Y%m%d', time.localtime(time.time()))].create_index(
            [('id', pymongo.ASCENDING)], unique=True)
        self.db[UserWeiboItem.collection + "_" + time.strftime('%Y%m%d', time.localtime(time.time()))].create_index(
            [('crawled_at', pymongo.DESCENDING)])
        self.db[UserWeiboItem.collection + "_" + time.strftime('%Y%m%d', time.localtime(time.time()))].create_index(
            [('user_id', pymongo.ASCENDING)])

        self.db[WeiboItem.collection].create_index([('id', pymongo.ASCENDING)], unique=True)
        self.db[WeiboItem.collection].create_index([('user_id', pymongo.ASCENDING)])
        self.db[WeiboItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[RepostItem.collection].create_index([('id', pymongo.ASCENDING)], unique=True)
        self.db[RepostItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[AttitudeItem.collection].create_index([('id', pymongo.ASCENDING)], unique=True)
        self.db[AttitudeItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[CommentNewItem.collection].create_index([('id', pymongo.ASCENDING)], unique=True)
        self.db[CommentNewItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[UserDetailItem.collection].create_index([('id', pymongo.ASCENDING)], unique=True)
        self.db[UserDetailItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[UserAttentionMemberItem.collection].create_index(
            [('id', pymongo.ASCENDING), ('user_id', pymongo.ASCENDING)], unique=True)
        self.db[UserAttentionMemberItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

        self.db[UserAttentionTagItem.collection].create_index([('user_id', pymongo.ASCENDING)], unique=True)
        self.db[UserAttentionTagItem.collection].create_index([('crawled_at', pymongo.DESCENDING)])

    def close_spider(self, spider):
        """
        close conn
        :param spider:
        :return:
        """
        self.client.close()

    def _process_item(self, item, spider):

        """
        用户成员标签，获取用户信息，存入用户表，清楚user对象
        存入表
        """
        if isinstance(item, UserAttentionTagItem):
            data = item.get("data")
            user = data.get('user')
            user_id = data.get("user_id")
            if user:
                screen_name = user.get("screen_name")
                # self.db['users'].update_one({'id': user_id}, {'$set': user}, upsert=True)
                result = self.db['users'].update_one({'id': user.get("id")}, {'$set': user})
                logging.debug(f'update user {user_id},{screen_name},{result.modified_count}')
                del data['user']
            self.db[item.collection].update_one({'user_id': data.get('user_id')}, {'$set': data}, upsert=True)
            logging.debug(f'saved to mongo: {item.collection} {data.get("user_id")}')

        """
        用户兴趣成员，直接存入表
        """
        if isinstance(item, UserAttentionMemberItem):
            data = item.get("data")
            self.db[item.collection].update_one(
                {'id': data.get('id')}, {'$set': data}, upsert=True)
            logging.debug(
                f'saved to mongo: {item.collection} {data.get("id")} {data.get("user_id")} {data.get("tag_id")}')

        """
        微博信息，清理用户信息，存入表
        """
        if isinstance(item, UserWeiboItem):
            data = item.get('data')
            user = data.get('user')
            if user:
                last_page = user.get("last_page")
                if last_page:
                    self.db['users'].update_one({'id': user.get("id")}, {'$set': user}, upsert=True)
                del data["user"]
            id = data.get('id')
            self.db[item.collection + "_" + time.strftime('%Y%m%d', time.localtime(time.time()))].update_one(
                {'id': id}, {'$set': data}, upsert=True)
            logging.debug(f'saved to mongo: {item.collection} id={id}')

        """
        微博信息，清理用户信息，存入表
        """
        if isinstance(item, WeiboItem):
            data = item.get('data')
            user = data.get('user')
            if user:
                del data["user"]
            id = data.get('id')
            self.db[item.collection].update_one({'id': id}, {'$set': data}, upsert=True)
            logging.debug(f'saved to mongo: {item.collection} id={id}')

        """
        评论转发点赞，将user对象存入users表，清理user对象
        从weibos表中查询weibo的user_id,存入weibo_user_id字段
        更新或者插入表
        """

        if isinstance(item, CommentNewItem) \
                or isinstance(item, RepostItem) \
                or isinstance(item, AttitudeItem):
            data = item.get('data')
            id = data.get('id')
            user = data.get('user')
            weibo_id = data.get("weibo")
            if user:
                user_id = user.get("id")
                screen_name = user.get("screen_name")
                logging.debug(f'update user {user_id},{screen_name}')
                self.db['users'].update_one({'id': user_id}, {'$set': user}, upsert=True)
                del data["user"]
            weibo = self.db[WeiboItem.collection].find({'id': weibo_id}).limit(1)
            if weibo:
                data["weibo_user_id"] = weibo[0].get("user_id")
            self.db[item.collection].update_one({'id': id}, {'$set': data}, upsert=True)
            logging.debug(f'saved to mongo: {item.collection} id={id}')

        """
        用户详情信息，直接如入表
        """
        if isinstance(item, UserDetailItem):
            data = item.get('data')
            id = data.get('id')
            self.db[item.collection].update_one({'id': id}, {'$set': data}, upsert=True)
            logging.debug(f'saved to mongo: {item.collection} id={id}')
        return item

    def process_item(self, item, spider):
        """
        process item using defer
        :param item:
        :param spider:
        :return:
        """
        return deferToThread(self._process_item, item, spider)


# class RedisPipeline(object):
#     """
#     pipeline for elasticsearch
#     """
#
#     def __init__(self, connection_string):
#         """
#         init connection_string and mappings
#         :param connection_string:
#         """
#         self.connection_string = connection_string
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         """
#         class method for pipeline
#         :param crawler: scrapy crawler
#         :return:
#         """
#         return cls(
#             connection_string=crawler.settings.get('REDIS_URL'),
#         )
#
#     def open_spider(self, spider):
#         """
#         open spider to do
#         :param spider:
#         :return:
#         """
#         self.conn = Redis(
#             hosts=[self.connection_string]
#         )
#
#     def _process_item(self, item, spider):
#         """
#         main process
#         :param item: user or weibo or comment item
#         :param spider:
#         :return:
#         """
#         if isinstance(item, UserDetailItem) or isinstance(item, UserAttentionItem) or isinstance(item,
#                                                                                                  UserAttentionMemberItem):
#             BloomFilter(self.conn, item.get("start_url_filter")).insert()
#             self.conn.index(index=item.index,
#                             id=item['id'],
#                             doc_type=item.type,
#                             body=dict(item), timeout=60)
#         return item
#
#     def process_item(self, item, spider):
#         """
#         process item using deferToThread
#         :param item:
#         :param spider:
#         :return:
#         """
#         return deferToThread(self._process_item, item, spider)


class RedisStartUrlFilterPipeline(object):
    """
    pipeline for 布隆过滤器
    """

    def __init__(self, connection_string):
        """
        init connection_string and mappings
        :param connection_string:
        """
        self.connection_string = connection_string

    @classmethod
    def from_crawler(cls, crawler):
        """
        class method for pipeline
        :param crawler: scrapy crawler
        :return:
        """
        return cls(
            connection_string=crawler.settings.get('REDIS_URL'),
        )

    def open_spider(self, spider):
        """
        open spider to do
        :param spider:
        :return:
        """
        self.conn = Redis.from_url(self.connection_string)

    def _process_item(self, item, spider):
        """
        main process
        :param item: user or weibo or comment item
        :param spider:
        :return:
        """
        if isinstance(item, UserDetailItem):
            user_id = item.get("data").get("id")
            url = UserDetailItem.url.format(user_id=user_id)
            BloomFilter(self.conn, UserDetailItem.start_url_filter).insert(url)

        if isinstance(item, UserWeiboItem):
            user_id = item.get("data").get("user_id")
            url = UserWeiboItem.url.format(uid=user_id, page=1)
            BloomFilter(self.conn, UserWeiboItem.start_url_filter).insert(url)

        if isinstance(item, UserAttentionTagItem):
            user_id = item.get("data").get("user_id")
            url = UserAttentionTagItem.url.format(user_id=user_id)
            BloomFilter(self.conn, UserAttentionTagItem.start_url_filter).insert(url)

        if isinstance(item, UserAttentionMemberItem) and item.get("first_row"):
            user_id = item.get("data").get("user_id")
            tag_id = item.get("data").get("tag_id")
            url = UserAttentionMemberItem.url.format(user_id=user_id, tag_id=tag_id)
            BloomFilter(self.conn, UserAttentionMemberItem.start_url_filter).insert(url)
        return item

    def process_item(self, item, spider):
        """
        process item using deferToThread
        :param item:
        :param spider:
        :return:
        """
        return deferToThread(self._process_item, item, spider)


class RedisStartUrlContinuePipeline(object):
    """
    pipeline for 布隆过滤器
    """

    def __init__(self, connection_string, init_users):
        """
        init connection_string and mappings
        :param connection_string:
        """
        self.connection_string = connection_string
        self.init_users = init_users

    @classmethod
    def from_crawler(cls, crawler):
        """
        class method for pipeline
        :param crawler: scrapy crawler
        :return:
        """
        return cls(
            connection_string=crawler.settings.get('REDIS_URL'),
            init_users=crawler.settings.get('INIT_USERS'),
        )

    def open_spider(self, spider):
        """
        open spider to do
        :param spider:
        :return:
        """
        self.conn = Redis.from_url(self.connection_string)

    def _process_item(self, item, spider):
        """
        main process
        :param item: user or weibo or comment item
        :param spider:
        :return:
        """
        if isinstance(item, WeiboItem):
            weibo_user_id = item.get("data").get("user_id")
            weibo_id = item.get("data").get("id")
            if str(weibo_user_id) in self.init_users:
                attitude_url = AttitudeItem.url.format(weibo_id=weibo_id, page=1)
                logging.debug(f"添加点赞页面{attitude_url}")
                self.conn.sadd(AttitudeItem.start_url, attitude_url)
                comment_url = CommentNewItem.url.format(id=weibo_id, max_id=0)
                logging.debug(f"添加评论页面{comment_url}")
                self.conn.sadd(CommentNewItem.start_url, comment_url)
                repost_url = RepostItem.url.format(id=weibo_id, page=1)
                logging.debug(f"添加转发页面{repost_url}")
                self.conn.sadd(RepostItem.start_url, repost_url)

        user_id = None
        if isinstance(item, AttitudeItem):
            # 爬取用户详情 和 用户关注列表
            user_id = item.get("data").get("user_id")
        if isinstance(item, CommentNewItem):
            # 爬取用户详情 和 用户关注列表
            user_id = item.get("data").get("user_id")
        if isinstance(item, RepostItem):
            # 爬取用户详情 和 用户关注列表
            user_id = item.get("data").get("user_id")
        if isinstance(item, UserAttentionMemberItem):
            # 爬取爬取用户详情
            member_id = item.get("data").get("id")
            user_detail_url = UserDetailItem.url.format(user_id=member_id)
            user_detail_exist = BloomFilter(self.conn, UserDetailItem.start_url_filter).exists(user_detail_url)
            if not user_detail_exist:
                logging.debug(f"添加用户详情页面{user_detail_url}")
                self.conn.sadd(UserDetailItem.start_url, user_detail_url)

        if user_id:
            weibo_url = UserWeiboItem.url.format(uid=user_id, page=1)
            weibo_url_exist = BloomFilter(self.conn, UserWeiboItem.start_url_filter).exists(weibo_url)
            if not weibo_url_exist:
                logging.debug(f"添加微博页面{weibo_url}")
                self.conn.sadd(UserWeiboItem.start_url, weibo_url)
            # screen_name = item.get("data").get("user").get("screen_name")
            # 用户名字是 用户1234543
            # if screen_name and not re.match("用户\d+", screen_name):
            user_detail_url = UserDetailItem.url.format(user_id=user_id)
            user_detail_exist = BloomFilter(self.conn, UserDetailItem.start_url_filter).exists(user_detail_url)
            if not user_detail_exist:
                logging.debug(f"添加用户详情页面{user_detail_url}")
                self.conn.sadd(UserDetailItem.start_url, user_detail_url)

            user_attention_tag_url = UserAttentionTagItem.url.format(user_id=user_id)
            user_attention_tag_exist = BloomFilter(self.conn, UserAttentionTagItem.start_url_filter).exists(
                user_attention_tag_url)
            if not user_attention_tag_exist:
                logging.debug(f"添加用户关注列表页面{user_attention_tag_url}")
                self.conn.sadd(UserAttentionTagItem.start_url, user_attention_tag_url)

        if isinstance(item, UserAttentionTagItem):
            user_id = item.get("data").get("user_id")
            tag_users_tops = item.get("data").get("tag_users_tops")
            for tag in tag_users_tops:
                tag_id = tag.get("tag_id")
                user_attention_member_url = UserAttentionMemberItem.url.format(user_id=user_id, tag_id=tag_id)
                user_attention_member_exist = BloomFilter(self.conn, UserAttentionMemberItem.start_url_filter).exists(
                    user_attention_member_url)
                if not user_attention_member_exist:
                    logging.debug(f"添加用户关注列表成员页面{user_attention_member_url}")
                    self.conn.sadd(UserAttentionMemberItem.start_url, user_attention_member_url)
        return item

    def process_item(self, item, spider):
        """
        process item using deferToThread
        :param item:
        :param spider:
        :return:
        """
        return deferToThread(self._process_item, item, spider)


# screen_name = "用户12312"
# if not re.match("用户\d+", screen_name):
#     print("ok")
# print(re.match("用户\d+", screen_name))
