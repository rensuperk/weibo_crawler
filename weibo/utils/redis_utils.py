#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2020/4/9
"""
import math
import time

import pymongo
import redis

from weibo.items import UserWeiboItem, UserDetailItem, UserAttentionTagItem, UserAttentionMemberItem
from weibo.settings import REDIS_URL, MONGO_DB, MONGO_URI
from weibo.utils.bloomfilter import bloomfilter
from weibo.utils.bloomfilter.bloomfilter import BloomFilter


class RedisClient(object):
    def __init__(self, connection_string=REDIS_URL, **kwargs):
        self.db = redis.StrictRedis.from_url(connection_string, decode_responses=True, **kwargs)


def copy_redis_keys(resource, target):
    client = RedisClient().db
    total = client.scard(resource)
    page_count = 10000
    total_page = math.ceil(total / page_count)
    for i in range(total_page):
        values = client.spop(resource, page_count)
        pip = client.pipeline()
        print(f"move {resource} to {target} {i} {total_page} {total}")
        for value in values:
            pip.sadd(target, value)
            pip.srem(resource, value)
        pip.execute()


def bak_weibo_filter():
    copy_redis_keys('m_attitude_redis:dupefilter', 'm_attitude_redis:dupefilter_bak1')
    copy_redis_keys('m_comment_redis:dupefilter', 'm_comment_redis:dupefilter_bak1')
    copy_redis_keys('m_repost_redis:dupefilter', 'm_repost_redis:dupefilter_bak1')
    copy_redis_keys('m_weibo_redis:dupefilter', 'm_weibo_redis:dupefilter_bak1')


def copy_local_to_bloom():
    client = redis.StrictRedis.from_url('redis://:@localhost:6379?db=0', decode_responses=True)
    test_client = RedisClient().db
    bloom_key = "m_user_weibo_redis:bloomfilter"
    from_key1 = "m_user_weibo_redis:dupefilter"
    from_key2 = "m_user_weibo_redis:dupefilter_bak1"
    from_key3 = "m_user_weibo_redis:dupefilter_bak2"
    from_key4 = "m_user_weibo_redis:dupefilter_bak3"
    # from_key5 = "m_user_weibo_redis:dupefilter_bak4"
    keys = [from_key1, from_key2, from_key3, from_key4]
    # keys = [from_key5]
    for key in keys:
        total = client.scard(key)
        page_count = 10000
        total_page = math.ceil(total / page_count)
        for i in range(total_page):
            print(f"{key} total: {i} {total_page} {total}")
            pip = client.pipeline()
            test_pip = test_client.pipeline()
            for value in client.spop(key, page_count):
                BloomFilter(test_client, bloom_key).insert_pipline(value, test_pip)
                pip.srem(key, value)
            pip.execute()
            test_pip.execute()


def check_boom_filter():
    client = RedisClient().db
    url = UserWeiboItem.url.format(uid=1000669513, page=1)
    exist = bloomfilter.BloomFilter(client, UserWeiboItem.start_url_filter).exists(url)
    print(exist)
    get = client.sismember(UserWeiboItem.start_url, url)
    print(f'exist start_urls{get}')


def rename_redis_keys():
    rename_keys('m_attitude_redis:dupefilter')
    rename_keys("m_comment_redis:dupefilter")
    rename_keys("m_repost_redis:dupefilter")
    rename_keys("m_weibo_redis:dupefilter")


def get_count():
    keys = ["m_user_weibo_redis:start_urls",
            "m_user_detail_redis:start_urls",
            "m_user_attention_member_redis:start_urls",
            "m_user_attention_tag_redis:start_urls",
            ]
    for key in keys:
        count = RedisClient().db.scard(key)
        print(f"{key}	{count}	{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")


def rename_keys(key):
    if RedisClient().db.exists(key):
        target = key + "_bak1"
        keys = RedisClient().db.keys(key + "_bak*")
        if keys:
            for i in range(1, 20):
                target = key + "_bak" + str(i)
                exist = False
                for exist_key in keys:
                    if target == exist_key:
                        exist = True
                        break
                if not exist:
                    break
        RedisClient().db.rename(key, target)


def add_user_detail():
    urls = [
        "https://weibo.com/ajax/profile/detail?uid=6027872293",
        "https://weibo.com/ajax/profile/detail?uid=6144299319",
        "https://weibo.com/ajax/profile/detail?uid=3082360781",
        "https://weibo.com/ajax/profile/detail?uid=1784139425",
        "https://weibo.com/ajax/profile/detail?uid=7271690479",
        "https://weibo.com/ajax/profile/detail?uid=1973858752",
        "https://weibo.com/ajax/profile/detail?uid=1711860984",
        "https://weibo.com/ajax/profile/detail?uid=2941415505",
        "https://weibo.com/ajax/profile/detail?uid=1092451687",
        "https://weibo.com/ajax/profile/detail?uid=5319744007",
        "https://weibo.com/ajax/profile/detail?uid=5974408474",
        "https://weibo.com/ajax/profile/detail?uid=7236991354",
        "https://weibo.com/ajax/profile/detail?uid=3774750064",
        "https://weibo.com/ajax/profile/detail?uid=2488292985",
        "https://weibo.com/ajax/profile/detail?uid=7220033486",
        "https://weibo.com/ajax/profile/detail?uid=7560350397",
        "https://weibo.com/ajax/profile/detail?uid=3256135891",
        "https://weibo.com/ajax/profile/detail?uid=6781387984",
        "https://weibo.com/ajax/profile/detail?uid=2576760820",
        "https://weibo.com/ajax/profile/detail?uid=3235268874",
        "https://weibo.com/ajax/profile/detail?uid=3591874391",
        "https://weibo.com/ajax/profile/detail?uid=5596497157",
        "https://weibo.com/ajax/profile/detail?uid=6888147162",
        "https://weibo.com/ajax/profile/detail?uid=2092785563",
        "https://weibo.com/ajax/profile/detail?uid=7070706510",
        "https://weibo.com/ajax/profile/detail?uid=1856637071",
        "https://weibo.com/ajax/profile/detail?uid=5529807724",
        "https://weibo.com/ajax/profile/detail?uid=2081358583",
        "https://weibo.com/ajax/profile/detail?uid=2702338033",
        "https://weibo.com/ajax/profile/detail?uid=6092490374",
        "https://weibo.com/ajax/profile/detail?uid=1204138405",
        "https://weibo.com/ajax/profile/detail?uid=7647116659",
        "https://weibo.com/ajax/profile/detail?uid=7400124685",
        "https://weibo.com/ajax/profile/detail?uid=2820242175"]
    for url in urls:
        RedisClient().db.sadd("m_user_detail_redis:start_urls", url)


def insert_weibo_id_user_id():
    weibos = pymongo.MongoClient(MONGO_URI)[MONGO_DB]["weibos"].find({}, {"id": 1, "user_id": 1})
    client = RedisClient().db
    pip = client.pipeline()
    for weibo in weibos:
        pip.hset("weibos_map", weibo.get("id"), weibo.get("user_id"))
    pip.execute()


def insert_user_detail_id():
    user_details = pymongo.MongoClient(MONGO_URI)[MONGO_DB]["user_detail"].find({}, {"id": 1})
    client = RedisClient().db
    pip = client.pipeline()
    print("开始插入user_detail_id")
    for user_detail in user_details:
        pip.sadd("user_detail_id", UserAttentionTagItem.url.format(user_id=user_detail.get("id")))
    print("插入pip")
    pip.execute()
    print("pip执行完")


def insert_user_id():
    users = pymongo.MongoClient(MONGO_URI)[MONGO_DB]["users"].find({}, {"id": 1})
    client = RedisClient().db
    pip = client.pipeline()
    print("开始插入user_id")
    for user in users:
        pip.sadd("user_id", user.get("id"))
    print("插入pip")
    pip.execute()
    print("pip执行完")


def insert_user_attention_member():
    users = pymongo.MongoClient(MONGO_URI)[MONGO_DB][UserAttentionTagItem.collection].find()
    client = RedisClient().db
    pip = client.pipeline()
    print("开始插入insert_user_attention_tag")
    url = 'https://m.weibo.cn/api/attentionvist/groupsMembersByTag?to_uid={user_id}&tag_id={tag_id}&page=1&count=20&trim_status=0'
    for user in users:
        user_id = user.get("user_id")
        tag_users_tops = user.get("tag_users_tops")
        mem = client.sismember("user_attention_member_id", user_id)
        if not mem and tag_users_tops:
            print(f"{user_id} insert member")
            for tag_users_top in tag_users_tops:
                tag_id = tag_users_top.get("tag_id")
                pip.sadd(UserAttentionMemberItem.start_url, url.format(user_id=user_id, tag_id=tag_id))
    print("插入pip")
    pip.execute()
    print("pip执行完")


def insert_user_no_friends_count_id():
    # users = pymongo.MongoClient(MONGO_URI)[MONGO_DB]["users"].count_documents({"friends_count":None})
    # print(users)
    users = pymongo.MongoClient(MONGO_URI)[MONGO_DB]["users"].find({"friends_count": None}, {"id": 1})
    client = RedisClient().db
    pip = client.pipeline()
    print("开始插入user_id")
    for user in users:
        pip.sadd("user_no_friends_count_id", UserAttentionTagItem.url.format(user_id=user.get("id")))
    print("插入pip")
    pip.execute()
    print("pip执行完")


def sdiff_user_no_fridends_count_and_user_no_exist():
    client = RedisClient().db
    not_exist_user_ids = client.smembers("not_exist_user_id")
    pip = client.pipeline()
    for not_exist_user_id in not_exist_user_ids:
        pip.sadd("not_exist_user_id_url", UserAttentionTagItem.url.format(user_id=not_exist_user_id))
    pip.execute()
    client.sdiff(UserAttentionTagItem.start_url, "user_no_friends_count_id", "not_exist_user_id_url")


def sinter_start_and_user():
    client = RedisClient().db
    dif_ids = client.sinterstore(UserAttentionTagItem.start_url + "bak", "user_detail_id", "user_no_friends_count_id")
    print("pip执行完")


def dif_user_detail_id():
    client = RedisClient().db
    dif_ids = client.sdiff("user_id", "user_detail_id")
    pip = client.pipeline()
    print("开始插入user_id")
    for dif_id in dif_ids:
        url = UserDetailItem.url.format(user_id=dif_id)
        pip.sadd(UserDetailItem.start_url, url)
    print("插入pip")
    pip.execute()
    print("pip执行完")


if __name__ == '__main__':
    # mode = sys.argv[1]
    # if mode == 'weibo':
    #     copy_local_to_bloom()
    # elif mode == 'attitude':
    #     copy_redis_keys('m_attitude_redis:dupefilter_bak', 'm_attitude_redis:dupefilter')
    # elif mode == 'comment':
    #     copy_redis_keys("m_comment_redis:dupefilter_bak", "m_comment_redis:dupefilter")
    # elif mode == 'repost':
    #     copy_redis_keys("m_repost_redis:dupefilter_bak", "m_repost_redis:dupefilter")
    # elif mode == 'rename':
    #     rename_redis_keys()
    get_count()
    # sdiff_user_no_fridends_count_and_user_no_exist()
    insert_user_attention_member()
    # insert_user_detail_id()
    # insert_user_no_friends_count_id()
    # sinter_start_and_user()

    # dif_user_detail_id()
    # insert_user_id()
    # check_boom_filter()
    # add_user_detail()
    # insert_weibo_id_user_id()
