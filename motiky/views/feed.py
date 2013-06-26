# -*- coding: utf-8 -*-
# author: notedit <notedit@gmail.com>
# date: 2013-04-10

import sys 
import time
import logging
import flask
from flask import g
from flask import request
from flask import Blueprint
from flask import redirect
from flask import Response
from flask import current_app
from flask import session
from flask import jsonify
from flask import flash
from flask.views import MethodView
from flask.views import View

from motiky import authutil
from motiky.logic import backend
from motiky.coreutil import BackendError
from motiky.configs import redis

instance = Blueprint('feed',__name__)

FEED_UPDATE_TIME_KEY = 'FEED::UPDATETIME::%(user_id)s'

def pipe_load(feeds):
    # todo some pipe load
    feeds_ret = []
    for po in feeds:
        try:
            user = backend.get_user(po['author_id'])
            po['user'] = user
            po['like_count'] = backend.get_post_liked_count(po['id'])
            po['comment_count'] = backend.get_post_comment_count(po['id']) 
        except BackendError,ex:
            continue
    return feeds

class NewFeedView(MethodView):

    def get(self,user_id):
        feed_time_meta = redis.hgetall(FEED_UPDATE_TIME_KEY % {'user_id':user_id})
        try:
            last_update_time = int(feed_time_meta.get('last_update_time'))
        except:
            last_update_time = int(time.time())

        last_update_time = datetime.fromtimestamp(last_update_time)
        res = backend.get_new_feed(user_id,last_update_time)
        return jsonify(has_new=res)

class FeedsView(MethodView):

    def get(self,user_id):
        try:
            page = int(request.values.get('page'))
        except:
            page = 1

        limit = 10
        offset = (page-1) * limit
        
        feeds = backend.get_latest_feed(user_id,limit,offset)

        if len(feeds) > 0:
            feeds = pipe_load(feeds)   
        
        curr_user = backend.get_user_by_uid(g.ukey)
        liked_post_ids = [p['id'] for p in feeds]
        liked_dict = backend.is_like_post(curr_user['id'],liked_post_ids)
        for up in feeds:
            up['is_like'] = liked_dict.get(up['id']) or False

        if page == 1:
            redis.hset(FEED_UPDATE_TIME_KEY % {'user_id':user_id},
                                'last_update_time',int(time.time()))
        return jsonify(results=feeds,page=page)

instance.add_url_rule('/feeds/<int:user_id>',view_func=FeedsView.as_view('feed'))
instance.add_url_rule('/feeds/notify/<int:user_id>',view_func=NewFeedView.as_view('feed_notify'))
