# -*- coding: utf-8 -*-
import logging
import time

import urllib3
from environs import Env

urllib3.disable_warnings()
logging.getLogger('py.warnings').setLevel(logging.ERROR)
logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
logging.getLogger('elasticsearch').setLevel(logging.INFO)
logging.getLogger('universal').setLevel(logging.INFO)
env = Env()
env.read_env()

# Scrapy settings for weibo project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'weibo'

SPIDER_MODULES = ['weibo.spiders']
NEWSPIDER_MODULE = 'weibo.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'weibo (+http://www.yourdomain.com)'
# Obey robots.txt rules 如果是true,基本不会爬取
ROBOTSTXT_OBEY = False
# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
    'Connection': 'keep-alive',
    # 'Host': 'm.weibo.cn',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}
RANDOMIZE_DOWNLOAD_DELAY = True
# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32
# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.15
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = True
# COOKIES_DEBUG = True
# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'weibo.middlewares.WeiboSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 101,
    'weibo.middlewares.CookieMiddleware': 100,
    'weibo.middlewares.RedirectMiddleware': 200,
    # 'weibo.middlewares.ProxypoolMiddleware': 300,
    # 'weibo.middlewares.ProxyDecreaseMiddleware': 600,
    # 'scrapy.middlewares.UserAgentMiddleware': None,
    # 'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': None,
    # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
    # 'weibo.middlewares.CookieMiddleware': 300,
    # 'weibo.middlewares.RedirectMiddleware': 200,
    # 'weibo.middlewares.RetryCommentMiddleware': 200,
    # 'middlewares.IPProxyMiddleware': 100,
    # 'weibo.middlewares.ProxypoolMiddleware': 100,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 101,

    # 重试中间件
    # 'weibo.middlewares.RetryCommentMiddleware': 551,
    # IP代理中间件
    # 'weibo.middlewares.ProxypoolMiddleware': 555 if env.bool('PROXYPOOL_ENABLED', True) else None,
    # 'weibo.middlewares.ProxytunnelMiddleware': 556 if env.bool('PROXYTUNNEL_ENABLED', True) else None,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
EXTENSIONS = {
    # 'scrapy_jsonrpc.webservice.WebService': 499,
    # 'scrapy_prometheus_exporter.prometheus.WebService': 500,
}

# COOKIES_ENABLED = False

# DOWNLOAD_DELAY = 10

# Configure item pipelines
ITEM_PIPELINES = {
    'weibo.pipelines.RecentTimePipeline': 100,
    'weibo.pipelines.TimePipeline': 300,
    'weibo.pipelines.RedisStartUrlContinuePipeline': 398,
    'weibo.pipelines.RedisStartUrlFilterPipeline': 399,
    'weibo.pipelines.MongoPipeline': 400,
}
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# definition of distributed
SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# REDIS_URL = env.str('REDIS_CONNECTION_STRING')
REDIS_URL = 'redis地址，单机模式'

# 去重持久化
# Don't cleanup redis queues, allows to pause/resume crawls.
SCHEDULER_PERSIST = True
# 重新爬取
SCHEDULER_FLUSH_ON_START = False
REDIS_START_URLS_AS_SET = True
# DUPEFILTER_DEBUG = True

# REDIS_START_URLS_BATCH_SIZE = 5
# SCHEDULER_QUEUE_KEY = 'weibo:%(spider)s:requests'
# SCHEDULER_DUPEFILTER_KEY = 'weibo:%(spider)s:dupefilter'

# definition of retry
RETRY_HTTP_CODES = [401, 403, 408, 414, 418, 500, 502, 503, 504]
PROXY_DECREASE_HTTP_CODES = [307, 408, 414, 418, 500, 502, 503, 504]
PROXY_MAX_HTTP_CODES = [200, 206, 302]
RETRY_TIMES = 20
DOWNLOAD_TIMEOUT = 20

# definition of proxy
# PROXYPOOL_URL = env.str('PROXYPOOL_URL')
PROXYPOOL_URL = '代理池接口'
# PROXY_DECREASE_URL = env.str('PROXY_DECREASE_URL')
PROXY_DECREASE_URL = '代理池减少分接口'
PROXY_MAX_URL = '代理池设置为最大分接口'
# PROXYTUNNEL_URL = env.str('PROXYTUNNEL_URL')

# definition of elasticsearch
# ELASTICSEARCH_CONNECTION_STRING = env.str('ELASTICSEARCH_CONNECTION_STRING')

MONGO_URI = 'mongo地址'
# MONGO_DB = env.str('MONGO_DB')
MONGO_DB = 'weibo'

# DINGTALK_TOKEN = env.str('DINGTALK_TOKEN')
DINGTALK_TOKEN = '通知'
# DINGTALK_SECRET = env.str('DINGTALK_SECRET')
DINGTALK_SECRET = '通知'

# DINGTALK_TOKEN = env.str('DINGTALK_TOKEN')
COOKIE_DINGTALK_TOKEN = '通知2'
# DINGTALK_SECRET = env.str('DINGTALK_SECRET')
COOKIE_DINGTALK_SECRET = '通知2'

LOG_LEVEL = 'INFO'
LOG_FILE = f'./logs/scrapy_{time.strftime("%Y-%m-%d")}.log'
LOG_STDOUT = True

INIT_USERS = (
    # 奥迪
    # "1841218153",
    # 梅赛德斯_奔驰
    # "1666454854",
    # 别克
    # "1667553532",
    # 广汽丰田
    # "1647951825",
    # 一汽丰田
    # "2286596480",
    # LEXUS雷克萨斯中国
    # "1931835691",
    # 保时捷
    # "3063296203",
    # 高合汽车
    # "7307620125",
    # 蔚来
    # "5675889356",
    # 宝马中国
    # "1698264705",
    # Patagonia中国官方微博
    # "2008912325",
    # 江诗丹顿
    # "3236334782",
    # Burberry
    # "1924007153",
    # Versace范思哲官方微博
    # "2356563467",
    # HERMES
    # "5223423947",
    # 马爹利MARTELL
    # "3973906499",
    # 轩尼诗Hennessy
    # "1801462015",
    # ARCTERYX始祖鸟
    # "3009471204",
    # 爱彼AudemarsPiguet
    # "3115261414",


    #劳斯莱斯汽车
    "3225131442",
    #宾利汽车中国
    "2682448731",
    #法拉利中国
    "2062260913",
    #路虎中国
    "2271357522",
    #玛莎拉蒂_Maserati
    "2044549283",
    #LEXUS雷克萨斯中国
    "1931835691",
    #兰博基尼汽车中国
    "1760603795",
    #林肯中国
    "5035483816",
    #PIAGET伯爵
    "2043491874",
    #积家JaegerLeCoultre
    "2367783340",


    #香奈儿CHANEL
    "1892475055",
    #路易威登
    "1836003984",
    #DIOR迪奥
    "2130860695",
    #Ferragamo菲拉格慕
    "2133330900",
    #Versace范思哲官方微博
    "2356563467",
    #Prada普拉达
    "5813211408",
    #FENDI
    "2826120835",
    #Armani阿玛尼
    "2411637190",
    #GUCCI
    "1934738161",
    #Zegna杰尼亚官方微博
    "2591168064",
    #卡地亚
    "2142012291",
    #VanCleefArpels梵克雅宝
    "2653491890",
    #Boucheron宝诗龙
    "2823454334",
    #海瑞温斯顿HarryWinston
    "2510493882",
    #尚美巴黎CHAUMET
    "2155043231",
    #BVLGARI宝格丽
    "2090537982",
    #MONTBLANC万宝龙
    "2313499034",
    #TiffanyAndCo蒂芙尼
    "2492431184",
    #MIKIMOTO御木本
    "1913756042",
    #BLANCPAIN瑞士宝珀腕表
    "2102760441",
    #格拉苏蒂原创
    "2131330371",
    #BREGUET宝玑
    "5203473260",
    #ROLEX劳力士
    "6273255109",
    #FRANCKMULLER法穆兰
    "5662540037",
    #香奈儿美妆
    "6444188526",
    #DIOR迪奥美妆
    "6106083314",
    #Guerlain法国娇兰
    "1874305853",
    #GIVENCHY纪梵希美妆
    "1922825090",
    #HR赫莲娜
    "1862278082",
    #Sisley法国希思黎
    "1901597310",
    #LaPrairie莱珀妮
    "1770149667",
    #LAMER海蓝之谜
    "1689520375",
    #兰蔻LANCOME
    "1742666164",
    #碧欧泉Biotherm
    "1745068231",
    #乐顺游艇Lurssen
    "7280540892",
    #意大利法拉帝集团
    "1878522022",
    #阿斯顿马丁中国
    "2615253663",
    #阿斯顿马丁上海
    "2291428742",
    #SSCC中国超跑俱乐部
    "1827245184",
    #世爵SPYKER-中国
    "2043012915",
    #帕加尼中国
    "5083476655",
    #科尼赛克中国
    "6539194057",
    #IWC万国表
    "2004738083",
    #路易十三LOUISXIII
    "1762247545",
    #轩尼诗Hennessy
    "1801462015",
    #麦卡伦TheMacallan
    "7369989514",
    #PerrierJouet美丽时光
    "6444426726",
    #哈雷戴维森_中国
    "2093572551",
    #BOSE
    "2359460160",
    #VERTU纬图
    "3229027917",
    #施坦威Steinway
    "2597701651",
    #博兰斯勒钢琴Bluthner
    "3202577384",
    #赛格威全地形车
    "7458306374",
    #SHANGXIA上下
    "1670480830",
)
