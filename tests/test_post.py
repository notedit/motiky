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

class TestPost(TestCase):


    def test_post_view(self):

        # post
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        headers = self.generate_header('weibo_id01')
        data = {
                'title':'title01',
                'author_id':user1['id'],
                'video_file':(StringIO('AAAA' * 10000),'hello.mp4'),
                'pic_file':(StringIO('AAAA' * 1000),'hello.png')
                }

        resp = self.client.post('/post',data=data,headers=headers)

        _data = json.loads(resp.data)
        assert resp.status_code == 200
        assert _data['title'] == 'title01'

        # get
        resp = self.client.get('/post/%d' % _data['id'],headers=headers)
        data_get = json.loads(resp.data)
        print resp.data
        assert data_get['title'] == 'title01'

        # put
        put_in = {'pic_small':'pic_small'}
        resp = self.client.put('/post/%d'%_data['id'],data=json.dumps(put_in),
                                headers=headers,content_type='application/json')
        print resp.data
        assert resp.status_code == 204

    def test_posts_view(self):

        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                        'video_url','pic_small1')
        post2 = backend.add_post('post02',user1['id'],
                        'video_url','pic_small2')
        post3 = backend.add_post('post03',user1['id'],
                        'video_url','pic_small3')

        headers = self.generate_header('weibo_id01')

        resp = self.client.get('/posts',headers=headers)
        data_get = json.loads(resp.data)
        assert len(data_get['posts']) == 3

    def test_user_posts(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                            'video_url','pic_small1')
        post2 = backend.add_post('post02',user1['id'],
                            'video_url','pic_small2')
        post3 = backend.add_post('post03',user1['id'],
                            'video_url','pic_small3')

        headers = self.generate_header('weibo_id01')

        resp = self.client.get('/posts/user/%d'%user1['id'],headers=headers)
        data_get = json.loads(resp.data)
        assert len(data_get['posts']) == 3

    def test_user_liked_posts(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                                'video_url','pic_small1')
        post2 = backend.add_post('post02',user1['id'],
                                'video_url','pic_small2')
        post3 = backend.add_post('post03',user1['id'],
                                'video_url','pic_small3')

        headers = self.generate_header('weibo_id01')

        ula1 = UserLikeAsso(user_id=user1['id'],post_id=post1['id'])
        ula2 = UserLikeAsso(user_id=user1['id'],post_id=post2['id'])
        ula3 = UserLikeAsso(user_id=user1['id'],post_id=post3['id'])

        db.session.add(ula1)
        db.session.add(ula2)
        db.session.add(ula3)
        db.session.commit()

        resp = self.client.get('/posts/user/%d/liked'%user1['id'],headers=headers)
        data_get = json.loads(resp.data)
        assert len(data_get['posts']) == 3

    def test_post_like(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        post1 = backend.add_post('post01',user1['id'],
                                'video_url','pic_small1')

        headers = self.generate_header('weibo_id01')

        _data = {
                'user_id':user1['id'],
                'post_id':post1['id']
                }
        resp = self.client.post('/post/like',data=json.dumps(_data),
                headers=headers,content_type='application/json')

        data_get = json.loads(resp.data)
        assert data_get['like_count'] == 1


        resp = self.client.post('/post/unlike',data=json.dumps(_data),
                headers=headers,content_type='application/json')

        data_get = json.loads(resp.data)
        assert data_get['like_count'] == 0
