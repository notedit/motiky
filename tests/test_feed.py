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

class TestFeed(TestCase):


    def test_feeds_view(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')
        user3 = backend.add_user('username03','photo_url03','weibo_id03') 
        user4 = backend.add_user('username04','photo_url04','weibo_id04')

        post1 = backend.add_post('title01',user1['id'],'video_url01',
                    pic_small='pic_small01')
        post2 = backend.add_post('title02',user2['id'],'video_url02',
                    pic_small='pic_small')
        post3 = backend.add_post('title03',user3['id'],'video_url03',
                    pic_small='pic_small03')
        post4 = backend.add_post('title04',user4['id'],'video_url04',
                    pic_small='pic_small04')

        backend.follow_user(user4['id'],user1['id'])
        backend.follow_user(user4['id'],user2['id'])

        headers = self.generate_header('weibo_id04')

        resp = self.client.get('/feeds/%d' % user4['id'],headers=headers)
        ret = json.loads(resp.data)
        assert len(ret['results']) == 3


        backend.set_post(post3['id'],{'recommended':True})

        resp = self.client.get('/feeds/%d'% user4['id'],headers=headers)
        ret = json.loads(resp.data)

        assert len(ret['results']) == 4


