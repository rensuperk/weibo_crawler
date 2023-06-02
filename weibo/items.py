# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class UserItem(Item):
    collection = 'users'
    index = 'weibo-users'
    type = 'user'
    start_url = 'm_user_redis:start_urls'
    start_url_filter = 'm_user_redis:filter'
    data = Field()


# crawled_at = Field()
#
# avatar_hd = Field()
# close_blue_v = Field()
# cover_image_phone = Field()
# description = Field()
# follow_count = Field()
# follow_me = Field()
# followers_count = Field()
# followers_count_str = Field()
# following = Field()
# gender = Field()
# id = Field()
# like = Field()
# like_me = Field()
# mbrank = Field()
# mbtype = Field()
# profile_image_url = Field()
# profile_url = Field()
# screen_name = Field()
# statuses_count = Field()
# urank = Field()
# verified = Field()
# verified_reason = Field()
# verified_type = Field()
# verified_type_ext = Field()


class UserDetailItem(Item):
    collection = 'user_detail'
    index = 'weibo-user-detail'
    type = 'user_detail'
    start_url = 'm_user_detail_redis:start_urls'
    start_url_filter = 'm_user_detail_redis:filter'
    url = 'https://weibo.com/ajax/profile/detail?uid={user_id}'
    data = Field()
    # sunshine_credit = Field()
    # career = Field()
    # education = Field()
    # birthday = Field()
    # created_at = Field()
    # description = Field()
    # gender = Field()
    # ip_location = Field()
    # followers = Field()
    # label_desc = Field()
    # desc_text = Field()
    # verified_url = Field()
    # id = Field()
    # crawled_at = Field()


# class UserAttentionItem(Item):
#     collection = 'user_attention'
#     index = 'weibo-user-attention'
#     type = 'user_attention'
#     start_url = 'm_user_attention_redis:start_urls'
#     start_url_filter = 'm_user_attention_redis:filter'
#     url = 'https://m.weibo.cn/api/attentionvist/tagUsersCounts?to_uid={id}'
#     data = Field()
#     first_row = Field()
#     # sunshine_credit = Field()
#     # career = Field()
#     # education = Field()
#     # birthday = Field()
#     # created_at = Field()
#     # description = Field()
#     # gender = Field()
#     # ip_location = Field()
#     # followers = Field()
#     # label_desc = Field()
#     # desc_text = Field()
#     # verified_url = Field()
#     # id = Field()
#     # crawled_at = Field()

class UserAttentionTagItem(Item):
    collection = 'user_attention_tag'
    index = 'weibo-user-attention-tag'
    type = 'user_attention_tag'
    start_url = 'm_user_attention_tag_redis:start_urls'
    start_url_filter = 'm_user_attention_tag_redis:filter'
    url = 'https://m.weibo.cn/api/attentionvist?uid={user_id}'
    data = Field()
    # first_row = Field()
    # sunshine_credit = Field()
    # career = Field()
    # education = Field()
    # birthday = Field()
    # created_at = Field()
    # description = Field()
    # gender = Field()
    # ip_location = Field()
    # followers = Field()
    # label_desc = Field()
    # desc_text = Field()
    # verified_url = Field()
    # id = Field()
    # crawled_at = Field()


class UserAttentionMemberItem(Item):
    # collection = 'user_attention_member'
    collection = 'users'
    index = 'weibo-user-attention-member'
    type = 'user_attention_member'
    start_url = 'm_user_attention_member_redis:start_urls'
    start_url_filter = 'm_user_attention_member_redis:filter'
    url = 'https://m.weibo.cn/api/attentionvist/groupsMembersByTag?to_uid={user_id}&tag_id={tag_id}&page=1&count=200&trim_status=0'
    first_row = Field()
    data = Field()
    # sunshine_credit = Field()
    # career = Field()
    # education = Field()
    # birthday = Field()
    # created_at = Field()
    # description = Field()
    # gender = Field()
    # ip_location = Field()
    # followers = Field()
    # label_desc = Field()
    # desc_text = Field()
    # verified_url = Field()
    # id = Field()
    # crawled_at = Field()


class UserWeiboItem(Item):
    # collection = 'user_weibos'
    collection = 'user_weibos'
    # collection = 'user_weibos3'
    index = 'user-weibo-weibos'
    type = 'user-weibo'
    start_url = 'm_user_weibo_redis:start_urls'
    start_url_filter = 'm_user_weibo_redis:filter'
    url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    data = Field()
    first_row = Field()
    # user_id = Field()
    # created_at = Field()
    # crawled_at = Field()
    #
    # id = Field()
    # attitudes_count = Field()
    # mid = Field()
    # can_edit = Field()
    # show_additional_indication = Field()
    # text = Field()
    # source = Field()
    # favorited = Field()
    # pic_ids = Field()
    # is_paid = Field()
    # mblog_vip_type = Field()
    # user = Field()
    # pid = Field()
    # pidstr = Field()
    # retweeted_status = Field()
    # reposts_count = Field()
    # comments_count = Field()
    # picture = Field()
    # pictures = Field()
    # raw_text = Field()
    # thumbnail = Field()


class WeiboItem(Item):
    collection = 'weibos'
    index = 'weibo-weibos'
    type = 'weibo'
    start_url = 'm_weibo_redis:start_urls'
    start_url_filter = 'm_weibo_redis:filter'
    url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&page={page}&containerid=107603{uid}'
    data = Field()
    first_row = Field()
    # user_id = Field()
    # created_at = Field()
    # crawled_at = Field()
    #
    # id = Field()
    # attitudes_count = Field()
    # mid = Field()
    # can_edit = Field()
    # show_additional_indication = Field()
    # text = Field()
    # source = Field()
    # favorited = Field()
    # pic_ids = Field()
    # is_paid = Field()
    # mblog_vip_type = Field()
    # user = Field()
    # pid = Field()
    # pidstr = Field()
    # retweeted_status = Field()
    # reposts_count = Field()
    # comments_count = Field()
    # picture = Field()
    # pictures = Field()
    # raw_text = Field()
    # thumbnail = Field()


# https://m.weibo.cn/comments/hotflow?id=4792687805072260&mid=4792687805072260&max_id=514894093031438
# 每页20条，一般十几页就停止了
class CommentNewItem(Item):
    collection = 'comments'
    index = 'weibo-comments'
    type = 'comment'
    start_url = 'm_comment_redis:start_urls'
    start_url_filter = 'm_comment_redis:filter'
    url = 'https://m.weibo.cn/comments/hotflow?id={id}&mid={id}&max_id_type=0&max_id={max_id}'
    data = Field()
    first_row = Field()
    # user_id = Field()
    # weibo = Field()
    # crawled_at = Field()
    # created_at = Field()
    # id = Field()
    # rootid = Field()
    # rootidstr = Field()
    # floor_number = Field()
    # text = Field()
    # disable_reply = Field()
    # restrictOperate = Field()
    # source = Field()
    # comment_badge = Field()
    # user = Field()
    # mid = Field()
    # readtimetype = Field()
    # safe_tags = Field()
    # comments = Field()
    # max_id = Field()
    # total_number = Field()
    # isLikedByMblogAuthor = Field()
    # more_info_users = Field()
    # bid = Field()
    # like_counts = Field()
    # liked = Field()


# https://m.weibo.cn/api/comments/show?id=4792687805072260&page=50&count=100
# 每页10条，最多50页
class CommentOldItem(Item):
    collection = 'comments'
    index = 'weibo-comments'
    type = 'comment'
    user_id = Field()
    weibo = Field()
    crawled_at = Field()
    created_at = Field()

    id = Field()
    text = Field()
    source = Field()
    user = Field()
    like_counts = Field()
    liked = Field()
    reply_id = Field()
    reply_text = Field()


class AttitudeItem(Item):
    collection = 'attitudes'
    index = 'weibo-attitude'
    type = 'attitude'
    data = Field()
    url = 'https://m.weibo.cn/api/attitudes/show?id={weibo_id}&page={page}'
    start_url = 'm_attitude_redis:start_urls'
    start_url_filter = 'm_attitude_redis:filter'
    first_row = Field()
    # created_at = Field()
    # user_id = Field()
    # crawled_at = Field()
    #
    # id = Field()
    # source = Field()
    # user = Field()
    # cover = Field()
    # weibo = Field()


class RepostItem(Item):
    collection = 'reposts'
    index = 'weibo-reposts'
    type = 'repost'
    start_url = 'm_repost_redis:start_urls'
    start_url_filter = 'm_repost_redis:filter'
    url = 'https://m.weibo.cn/api/statuses/repostTimeline?id={id}&page={page}'
    data = Field()
    first_row = Field()
    # weibo = Field()
    # crawled_at = Field()
    # created_at = Field()
    # user_id = Field()
    # crawled_at = Field()
    #
    # id = Field()
    # mid = Field()
    # text = Field()
    # source = Field()
    # mblog_vip_type = Field()
    # pid = Field()
    # pidstr = Field()
    # retweeted_id = Field()
    # retweeted_status = Field()
    # user = Field()
    # reposts_count = Field()
    # comments_count = Field()
    # reprint_cmt_count = Field()
    # attitudes_count = Field()
    # pending_approval_count = Field()
    # isLongText = Field()
    # darwin_tags = Field()
    # hot_page = Field()
    # mblogtype = Field()
    # cardid = Field()
    # number_display_strategy = Field()
    # content_auth = Field()
    # comment_manage_info = Field()
    # repost_type = Field()
    # pic_num = Field()
    # new_comment_style = Field()
    # ab_switcher = Field()
    # region_name = Field()
    # region_opt = Field()
    # raw_text = Field()
    # bid = Field()
