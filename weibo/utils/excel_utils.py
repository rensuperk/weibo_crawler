import pandas as pd
import redis

from weibo.items import RepostItem
from weibo.settings import REDIS_URL
from weibo.utils import db_utils


def read_excel():
    df = pd.read_excel('../data/微博Cookie记录.xlsx')
    columns = df.columns.values.tolist()  ### 获取excel 表头 ，第一行
    accounts = {}
    for idx, row in df.iterrows():  ### 迭代数据 以键值对的形式 获取 每行的数据
        account = {}
        for column in columns:
            account[column] = row[column]
        if account.get("user_name"):
            accounts[account.get("user_name")] = account
    return accounts


def read_and_insert_lost_url(file_name, start_url):
    df = pd.read_csv(f'../data/{file_name}', sep=',', header=0, encoding='utf-8')
    redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)
    pip = redis_client.pipeline()
    for idx, row in df.iterrows():
        url = row["url"]
        pip.sadd(start_url, url)
    pip.execute()


def insert_cookie(accounts):
    for user_name in accounts:
        print(user_name, accounts[user_name])
        account = accounts[user_name]
        db_utils.insert_cookie(username=str(account.get("user_name")), name=account.get("name"), password="password",
                               m_cookie_str=account.get("m_cookie"), pc_cookie_str=account.get("pc_cookie"))


if __name__ == '__main__':
    # df = read_excel('./weibo/data/微博Cookie记录.xlsx')
    # accounts = read_excel()
    # insert_cookie(accounts)
    # read_text()
    # read_and_insert_lost_url("lost_user_detail.csv", UserDetailItem.start_url)
    read_and_insert_lost_url("lost_repost.csv", RepostItem.start_url)
    # read_and_insert_lost_url("lost_attitude.csv", AttitudeItem.start_url)
