# -*- coding: utf-8 -*-
# author: notedit <notedit@gmail.com>
# date: 2013-04-10

import sys 
import time
import logging
import traceback
from datetime import datetime

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
from motiky.cacheutil import rcache
from motiky.configs import rq,redis

instance = Blueprint('activity',__name__)

ACTIVITY_UPDATE_TIME_KEY = 'ACTIVITY::UPDATETIME::%(user_id)s'

# atype follow  like comment  post_reco text

def filter_activity(ac):
    # todo
    if ac['atype'] in ('follow','like','comment'):
        _user = rcache(3600*24)(backend.get_user)(ac['from_id'])
        ac.update({'user':_user})

    if ac['atype'] in ('like','comment','post_reco'):
        _post = rcache(3600*24)(backend.get_post)(ac['post_id'])
        ac.update({'post':_post})

    if ac['atype'] in ('comment'):
        _comment = rcache(3600*24)(backend.get_comment)(ac['comment_id'])
        ac.update({'comment':_comment})

    return ac

class UserNewActivityCountView(MethodView):

    def get(self,user_id):
        activity_time_meta = redis.hgetall(ACTIVITY_UPDATE_TIME_KEY % \
                                    {'user_id':user_id})
        try:
            last_update_time = int(activity_time_meta.get('last_update_time'))
        except:
            last_update_time = int(time.time())

        last_update_time = datetime.fromtimestamp(last_update_time)
        count = backend.get_new_activity_count(user_id,last_update_time)

        return jsonify(count=count)

class UserActivityView(MethodView):

    def get(self,user_id):
        acs = backend.get_activity_by_user(user_id)
        ac_list = []
        for ac in acs:
            try:
                ac = filter_activity(ac)
            except:
                traceback.print_exc()
                continue
            ac_list.append(ac)

        try:
            _user = backend.get_user(user_id)
        except BackendError,ex:
            traceback.print_exc()
        try:
            backend.set_install(user_id,{'badge':0})
            rq.enqueue('motiky.worker.apns_push',
                        user_id=user_id,data={
                            'badge':0
                            })
        except BackendError,ex:
            traceback.print_exc()

        redis.hset(ACTIVITY_UPDATE_TIME_KEY % {'user_id':user_id},
                        'last_update_time',int(time.time()))

        return jsonify(results=ac_list)

user_activity_func = UserActivityView.as_view('user_activity')
user_new_activity_count_func = UserNewActivityCountView.as_view('user_new_activity_count')

instance.add_url_rule('/user/<int:user_id>/activity',
        view_func=user_activity_func,methods=['GET'])

instance.add_url_rule('/user/<int:user_id>/activity/count',
        view_func=user_new_activity_count_func,methods=['GET'])



