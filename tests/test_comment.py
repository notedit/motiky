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

class TestComment(TestCase):


    def test_comment_view(self):

        # post
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        headers = self.generate_header('weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                        'video_url','pic_small1')

        data = {
                'author_id':user1['id'],
                'content':'comment01',
                'post_id':post1['id']
                }

        resp = self.client.post('/comment',data=json.dumps(data),headers=headers,
                            content_type='application/json')

        _data = json.loads(resp.data)
        assert resp.status_code == 200
        assert _data['content'] == 'comment01'
        
        # delete
        resp = self.client.delete('/comment/%d'%_data['id'],
                                headers=headers,content_type='application/json')
        print resp.data
        assert resp.status_code == 204

    def test_post_comment_view(self):

        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                        'video_url','pic_small1')
        comment1 = backend.add_comment(post1['id'],'comment1',user1['id'])
        comment2 = backend.add_comment(post1['id'],'comment2',user1['id'])
        comment3 = backend.add_comment(post1['id'],'comment3',user1['id'])

        headers = self.generate_header('weibo_id01')

        resp = self.client.get('/post/%d/comment' % post1['id'],headers=headers)
        data_get = json.loads(resp.data)
        assert len(data_get['comments']) == 3

