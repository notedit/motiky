# -*- coding: utf-8 -*-

import os
import sys
import types
import json
import time
from datetime import datetime
from datetime import timedelta

from StringIO import StringIO

from tests import TestCase


from motiky.logic.models import User,Post,UserLikeAsso,Report,Install,\
                UserFollowAsso,Comment,Activity,Action

from motiky.logic import backend

from motiky.configs import db,redis

class TestActivity(TestCase):


    def test_user_activity_view(self):

        # get
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        user2 = backend.add_user('username2','photo_url','weibo_id2')
        post1 = backend.add_post('title1',user1['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user1['id'],'video_url',
                    pic_small='pic_small')
        
        comment1 = backend.add_comment(post1['id'],'comment1',user1['id'])

        ac1 = {
                'post_id':post1['id'],
                'from_id':user1['id'],
                'to_id':user2['id'],
                'atype':'like'
                }
        ac2 = {
                'post_id':post1['id'],
                'from_id':user1['id'],
                'comment_id':comment1['id'],
                'to_id':user2['id'],
                'atype':'comment'
                }


        ret = backend.add_activity(ac1)
        ret = backend.add_activity(ac2)
        backend.new_install(user2['id'],'device_token')

        headers = self.generate_header('weibo_id2')
        resp = self.client.get('/user/%d/activity' % user2['id'],headers=headers)
        _data = json.loads(resp.data)
        assert resp.status_code == 200
        assert len(_data['results']) == 2

        redis.flushall()
        redis.hset('ACTIVITY::UPDATETIME::%(user_id)s' % {'user_id':user2['id']},
                                'last_update_time',int(time.time() - 3600 * 6))

        resp = self.client.get('/user/%d/activity/count' % user2['id'],
                headers=headers)
        _data = json.loads(resp.data)
        assert resp.status_code == 200
        assert _data['count'] == 2

        redis.hset('ACTIVITY::UPDATETIME::%(user_id)s' % {'user_id':user2['id']},
                                'last_update_time',int(time.time()) + 2)

        resp = self.client.get('/user/%d/activity/count' % user2['id'],
                headers=headers)
        _data = json.loads(resp.data)
        assert resp.status_code == 200
        assert _data['count'] == 0




        

