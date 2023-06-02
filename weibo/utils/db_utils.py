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
from datetime import datetime

import pymongo
import pytz
import redis
from pymongo.errors import DuplicateKeyError

from weibo.items import UserDetailItem, UserAttentionTagItem, UserAttentionMemberItem, UserWeiboItem, CommentNewItem
from weibo.settings import MONGO_URI, MONGO_DB, REDIS_URL
from weibo.utils.bloomfilter.bloomfilter import BloomFilter
from weibo.utils.redis_utils import RedisClient


class MongoClient(object):
    def __init__(self, db=MONGO_DB, connection_string=MONGO_URI, **kwargs):
        self.db = pymongo.MongoClient(connection_string)[db]


def insert_cookie(username, name, password, m_cookie_str, pc_cookie_str):
    """
    insert cookie to database
    :param username: username of weibo account
    :param password: password of weibo account
    :param cookie_str: cookie str
    :return:
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        pc_status = 'error'
        m_status = 'error'
        if pc_cookie_str:
            pc_status = 'success'
        if m_cookie_str:
            m_status = 'success'

        MongoClient().db['account'].insert_one(
            {"_id": username,
             "password": password,
             "name": name,
             "pc_cookie": pc_cookie_str,
             "m_cookie": m_cookie_str,
             "status": "success",
             "pc_status": pc_status,
             "m_status": m_status,
             "updated_at": now})
    except DuplicateKeyError as e:
        MongoClient().db['account'].find_one_and_update({'_id': username},
                                                        {'$set': {'pc_cookie': pc_cookie_str,
                                                                  "name": name,
                                                                  'm_cookie': m_cookie_str,
                                                                  "status": "success",
                                                                  "pc_status": pc_status,
                                                                  "m_status": m_status,
                                                                  "updated_at": now}})


def init_data(collection, query, group, columns, callback):
    collection = MongoClient().db[collection]
    total = collection.count_documents(query)
    page_size = 5000
    total_page = math.ceil(total / page_size)
    result = []
    for page in range(0, total_page):
        if group:
            records = collection.aggregate([
                {"$match": query}, {"$group": {"_id": group}}, {"$project": columns},
                {"$skip": page * page_size}, {"$limit": page_size}
            ])
        else:
            records = collection.find(query, columns).sort("crawled_at", 1).limit(page_size).skip(page * page_size)
        print(f'开始执行第{collection}{page}/{total_page}页')
        for record in records:
            callback(record)
    return result


def init_uer_detail_to_filter():
    bf = BloomFilter(RedisClient().db, UserDetailItem.start_url_filter)
    init_data(UserDetailItem.collection, {}, {'id': '$id'}, {'id': '$_id.id', "_id": 0},
              lambda record: bf.insert(UserDetailItem.url.format(user_id=record['id'])))


def init_user_attention_to_filter():
    bf = BloomFilter(RedisClient().db, UserAttentionTagItem.start_url_filter)
    init_data(UserAttentionTagItem.collection, {}, {"user_id": "$user_id"}, {"user_id": "$_id.user_id", "_id": 0},
              lambda record: bf.insert(UserAttentionTagItem.url.format(user_id=record['user_id'])))


def init_user_attention_member_to_filter():
    bf = BloomFilter(RedisClient().db, UserAttentionMemberItem.start_url_filter)
    init_data(UserAttentionMemberItem.collection, {}, {"user_id": "$user_id", "tag_id": "$tag_id"}
              , {"user_id": "$_id.user_id", "tag_id": "$_id.tag_id", "_id": 0},
              lambda record: bf.insert(
                  UserAttentionMemberItem.url.format(user_id=record['user_id'], tag_id=record['tag_id'])))


def init_weibo_to_filter():
    bf = BloomFilter(RedisClient().db, UserWeiboItem.start_url_filter)
    init_data(UserAttentionMemberItem.collection, {}, {"user_id": "$user_id"}
              , {"user_id": "$_id.user_id", "_id": 0},
              lambda record: bf.insert(UserWeiboItem.url.format(uid=record['user_id'], page=1)))


def update_comment_user_id(collection, record):
    collection = MongoClient().db[collection]
    collection.update_one({"id": record['id']}, {"$set": {"user_id": record.get('user').get('id')}})


def update_comments_user_id():
    init_data(CommentNewItem.collection, {"user_id": {"$exists": False}}, {}
              , {"user": "$user", "id": "$id", "user_id": "$user_id"},
              lambda record: update_comment_user_id(CommentNewItem.collection, record))


def create_index(collection):
    MongoClient().db[collection].create_index(
        [('id', pymongo.ASCENDING)], unique=True)
    MongoClient().db[collection].create_index(
        [('crawled_at', pymongo.DESCENDING)])
    MongoClient().db[collection].create_index(
        [('user_id', pymongo.ASCENDING)])


# create_index("user_weibos_20220803")
# create_index("user_weibos_20220804")
# create_index("user_weibos_20220805")
# create_index("user_weibos_20220806")
# create_index("user_weibos_20220807")


def merge_db(resource, target):
    query = {}
    columns = {}
    # return deferToThread(_merge_user, record)
    collection = MongoClient().db[resource]
    total = collection.count_documents({})
    page_size = 1000
    total_page = math.ceil(total / page_size)
    for page in range(0, total_page):
        records = collection.find(query, columns).sort("crawled_at", 1).limit(page_size).skip(page * page_size)
        print(f'开始执行第{collection}{page}/{total_page}页')
        request_many = []
        for record in records:
            del record['_id']
            request_many.append(pymongo.UpdateOne({"id": record['id']}, {"$set": record}, upsert=True))
        MongoClient().db[target].bulk_write(request_many, ordered=True)


def update_weibo_user_id(collection):
    query = {"weibo_user_id": {"$eq": None}}
    columns = {}
    collection_client = MongoClient().db[collection]
    # total = collection.count_documents(query)
    page_size = 5000
    # total_page = math.ceil(total / page_size)
    redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
    records = collection_client.find(query, columns).sort("crawled_at", 1)
    weibos_map = redis_client.hgetall("weibos_map")
    request_many = []
    j = 0
    for record in records:
        user_id = weibos_map.get(record.get("weibo"))
        if user_id:
            record['weibo_user_id'] = user_id
            request_many.append(pymongo.UpdateOne({"id": record['id']}, {"$set": record}))
        else:
            print(f'{collection}weibo_user_id not found {record.get("weibo")}')
        if len(request_many) >= page_size:
            j += 1
            collection_client.bulk_write(request_many)
            print(f'{collection}开始执行第{j}页')
            request_many = []
    if request_many:
        j += 1
        print(f'{collection}开始执行第{j}页')
        collection_client.bulk_write(request_many)


def insert_user_detail_start_urls():
    users_collection = MongoClient().db["users"]
    user_detail_collection = MongoClient().db["user_detail"]
    # query = {"screen_name": {"$not":{'$regex': '用户\d*$'}}}
    query = {}
    result = users_collection.find(query)
    redis_client = RedisClient().db
    # bf = BloomFilter(redis_client, UserDetailItem.start_url_filter)
    page_size = 500
    pip = redis_client.pipeline()
    i = 0
    for user in result:
        userId = user.get("id")
        url = UserDetailItem.url.format(user_id=userId)
        # exist = bf.exists(url)
        # if not exist:
        i += 1
        print(f"{userId} {len(pip.command_stack)} total:{i}")
        pip.sadd(UserDetailItem.start_url, url)
        if len(pip.command_stack) >= page_size:
            pip.execute()
    if len(pip.command_stack):
        pip.execute()


def insert_user_attention_tags_urls():
    users_collection = MongoClient().db["users"]
    user_attention_tag_collection = MongoClient().db["user_attention_tag"]
    # query = {"screen_name": {"$not":{'$regex': '用户\d*$'}}}
    query = {}
    result = users_collection.find(query)
    redis_client = RedisClient().db
    # bf = BloomFilter(redis_client, UserDetailItem.start_url_filter)
    page_size = 500
    pip = redis_client.pipeline()
    i = 0
    for user in result:
        userId = user.get("id")
        url = UserAttentionTagItem.url.format(user_id=userId)
        # exist = bf.exists(url)
        # if not exist:
        i += 1
        print(f"{userId} {len(pip.command_stack)} total:{i}")
        pip.sadd(UserAttentionTagItem.start_url, url)
        if len(pip.command_stack) >= page_size:
            pip.execute()
    if len(pip.command_stack):
        pip.execute()


def get_user_attention_member(max_time, pip, user_attention_member_handler, users_handler, member_user_id_handler):
    while True:
        # max_time = datetime.now(tz=pytz.utc)
        query = {"crawled_at": {"$lte": max_time}}
        # query = {"crawled_at": {"$gte": max_time}}
        group = {"user_id": "$user_id"}
        columns = {"user_id": 1, "_id": 0, "crawled_at": 1}
        # .sort({"crawled_at": -1000})
        # db.user_attention_member.find({crawled_at: {$lt: new ISODate("2022-07-31T15:03:48.510Z")}},{crawled_at:1,_id:0,user_id:1}).sort({"crawled_at": -1}).batchSize(100000)
        members = user_attention_member_handler.find(query, {}).limit(1000).sort([("crawled_at", -1)])
        list_member_id = []
        users_handler_list = []
        member_user_id_handler_list = []
        for member in members:
            max_time = member.get("crawled_at")
            # pip.sadd("user_attention_member_id", member.get("user_id"))
            id = member.get("id")
            user_detail_url = UserDetailItem.url.format(user_id=id)
            pip.sadd(UserDetailItem.start_url, user_detail_url)
            _id = member.get("_id")
            member.pop("_id")
            list_member_id.append(_id)
            users_handler_list.append(pymongo.UpdateOne({'id': id}, {'$set': member}, upsert=True))
            member_user_id_handler_list.append(pymongo.UpdateOne({'id': id}, {'$set': {"id": id}}, upsert=True))

        if not len(pip):
            print(f"没有{max_time},任务停止")
            return
        pip.execute()
        x = users_handler.bulk_write(users_handler_list)
        member_user_id_handler.bulk_write(member_user_id_handler_list)
        print("user插入了", x.upserted_count)

        y = user_attention_member_handler.delete_many({"_id": {"$in": list_member_id}})
        print("文档已经删除", y.deleted_count)
        print(f"{max_time} 开始下次查询")
        #get_user_attention_member(max_time, pip, user_attention_member_handler, users_handler, member_user_id_handler)


if __name__ == '__main__':
    # set_deep_crawler()
    # You can add cookie manually by the following code, change the value !!
    # insert_cookie(
    #     username='18500339447',
    #     name='邢雪霖',
    #     password='ORBtws829I4',
    #     m_cookie_str='SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWQH89FZskAMcn6cVLbiOcM5NHD95Qp1hBXeo54ehzNWs4Dqcjdi--4iKnEi-2Ei--ci-82i-2fi--Ri-2piKyh; WEIBOCN_FROM=1110006030; _T_WM=45864908612; SCF=At6sbrSr3JJ3p7HYcJ8_27PTcrIqOvsFAy5KO-YIhZvhDii4IUw7UM0tDeREAyUrw4WehthvDZxaDa7gOhIa6kQ.; SUB=_2A25P9ai3DeRhGedG71YT8CfMyTuIHXVtGcj_rDV6PUJbktANLW7_kW1NUSQ7eJBG-ljflM9uck1QYSU_pjrk9X3A; SSOLoginState=1660016871; XSRF-TOKEN=017960; mweibo_short_token=79db1808e1; MLOGIN=1; M_WEIBOCN_PARAMS=luicode=20000174&uicode=20000174',
    #     pc_cookie_str='SINAGLOBAL=97844667103.23293.1643194665290; SCF=At6sbrSr3JJ3p7HYcJ8_27PTcrIqOvsFAy5KO-YIhZvhcqFSG0Ry9qBIq_iCkrstWAtk1Plm38fimBk5tjjHI04.; UOR=,,spr_wbprod_sougou_sgss_weibo_t001; XSRF-TOKEN=eMVqppvgzVYNDimb-BMuvPuF; _s_tentry=weibo.com; Apache=9357999551682.48.1659594337327; ULV=1659594337368:17:4:4:9357999551682.48.1659594337327:1659512660831; ALF=1662608852; SSOLoginState=1660016871; SUB=_2A25P9ai3DeRhGedG71YT8CfMyTuIHXVtGcj_rDV8PUJbkNANLUP5kW1NUSQ7eCoX08RQiCmu8fNN9kxuwgcYp113; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWQH89FZskAMcn6cVLbiOcM5NHD95Qp1hBXeo54ehzNWs4Dqcjdi--4iKnEi-2Ei--ci-82i-2fi--Ri-2piKyh; WBPSESS=Dt2hbAUaXfkVprjyrAZT_LNrYGBapVjSozJB0gARPcHPyJS1kFCsoNT3wNL3T7AZE6GxablVQjE9ejOwrA5TeQlXUaZuTjcJ2zk_VbalIR_jzTx79WfQ4isxwR_rZDO4zdhMwWel4ICljh7jEK3YioRBxJEThg8DhMMvURzAb3wvhF3rkdmEV8XmtWEtp0QCvJYy_rksGlLntSr-8K1a6w==',
    # )
    # init_weibo_to_filter()
    # bf = BloomFilter(RedisClient().db, 'm_user_detail_redis:filter')
    # init_data('user_detail', {}, {'id': 1},
    #           lambda record: bf.insert(
    #               f'https://weibo.com/ajax/profile/detail?uid={record["id"]}'))
    # init_uer_detail()
    # init_uer_detail()
    # init_user_attention()
    # init_user_attention_member()
    # update_comments_user_id()
    # MongoClient().db["users"].create_index([('id', pymongo.ASCENDING)], unique=True)
    # MongoClient().db["users"].create_index([('crawled_at', pymongo.DESCENDING)])
    # merge_user()
    # merge_db("user_weibos_2022-08-02", "user_weibos_20220802")
    # update_weibo_user_id("attitudes")
    # update_weibo_user_id("comments")
    # update_weibo_user_id("reposts")
    # total = MongoClient().db["attitudes"].count_documents({"weibo_user_id": {"$exists":False}})
    # total = MongoClient().db["attitudes"].count_documents({"weibo_user_id": {"$eq":None}})
    # total = MongoClient().db["attitudes"].count_documents({"weibo_user_id": {"$eq":""}})
    # print(total)
    # insert_user_attention_tags_urls()

    # max_time = datetime.now(tz=pytz.utc)
    # max_time = datetime.strptime("2022-08-07 08:10:26.981000", "%Y-%m-%d %H:%M:%S")
    redis_client = RedisClient().db
    pip = redis_client.pipeline()
    user_attention_member_handler = MongoClient().db["user_attention_member"]
    users_handler = MongoClient().db["users"]
    member_user_id_handler = MongoClient().db["member_user_id"]
    # 2022-07-23 15:03:48.510000
    max_time = datetime(2022, 11, 23, 15, 3, 48, 510000)
    get_user_attention_member(max_time, pip, user_attention_member_handler, users_handler, member_user_id_handler)
    # min_time = datetime(2022,7,23,15,3,48,510)
    # min_time2 = datetime(2022,7,23,15,3,48,511)
    # if min_time2 > min_time:
    #     print("time")
