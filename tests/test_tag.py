# -*- coding: utf-8 -*-


import os
import sys
import types
import json
import time
from datetime import datetime
from datetime import timedelta

from tests import TestCase


from motiky.logic.models import User,Post,UserLikeAsso,Report,Install,\
                UserFollowAsso,Comment,Activity,Action,Tag,Tagging

from motiky.logic import backend

from motiky.configs import db,redis

class TestTag(TestCase):


    def test_tag_view(self):
        tag1 = Tag(name='tag1',show=True,pic_url='pic_url',
                recommended=True)
        tag2 = Tag(name='tag2',show=True,pic_url='pic_url',
                recommended=True)
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.commit()

        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                'video_url','pic_small1')
        post2 = backend.add_post('post02',user1['id'],
                'video_url','pic_small2')
        tagging1 = Tagging(taggable_type='post',taggable_id=post1['id'],tag_id=tag1.id)
        tagging2 = Tagging(taggable_type='post',taggable_id=post2['id'],tag_id=tag1.id)

        headers = self.generate_header('weibo_id01')
        # get
        resp = self.client.get('/tag/%d'% tag1.id,headers=headers)
        data_get = json.loads(resp.data)
        assert data_get['tag']['name'] == 'tag1'

        # get tags 
        resp = self.client.get('/tags',headers=headers)
        data_get = json.loads(resp.data)
        assert len(data_get['results']) == 2



