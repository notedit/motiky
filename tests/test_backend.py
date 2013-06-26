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

class TestUserLogic(TestCase):

    def test_get_user(self):
        user = User(username='username01',photo_url='photo_url01',uid='weibo_id01')
        db.session.add(user)
        db.session.commit()

        _user = backend.get_user(user.id)
        assert _user['username'] == user.username


    def test_add_user(self):
        user = backend.add_user('username','photo_url','weibo_id')
        assert user['username'] == 'username'

    def test_set_user(self):
        user = backend.add_user('username','photo_url','weibo_id')
        _user = backend.set_user(user['id'],{'username':'username2',
                                            'photo_url':'photo_url2'})
        assert _user['username'] == 'username2'

    def test_get_user_by_uid(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')
        
        user = backend.get_user_by_uid(user1['uid'])
        assert user['username'] == user1['username']

        users = backend.get_user_by_uid([user1['uid'],user2['uid']])
        assert len(users) == 2


    def test_follow_user(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')

        ret = backend.follow_user(user1['id'],user2['id'])
        assert ret > 0

    def test_unfollow_user(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')

        ret = backend.follow_user(user1['id'],user2['id'])

        ret = backend.unfollow_user(user1['id'],user2['id'])
        assert ret == True

    def test_is_following_user(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')

        backend.follow_user(user1['id'],user2['id'])
        ret = backend.is_following_user(user1['id'],user2['id'])
        assert ret == True

    def test_get_user_following(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')
        user3 = backend.add_user('username03','photo_url03','weibo_id03')

        backend.follow_user(user1['id'],user2['id'])
        backend.follow_user(user1['id'],user3['id'])

        users = backend.get_user_following(user1['id'])
        assert len(users) == 2

        count = backend.get_user_following_count(user1['id'])
        assert count == 2

    def test_get_user_follower(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        user2 = backend.add_user('username02','photo_url02','weibo_id02')
        user3 = backend.add_user('username03','photo_url03','weibo_id03')

        backend.follow_user(user2['id'],user1['id'])
        backend.follow_user(user3['id'],user1['id'])

        users = backend.get_user_follower(user1['id'])
        assert len(users) == 2
        
        count = backend.get_user_follower_count(user1['id'])
        assert count == 2
   

class TestPostLogic(TestCase):

    def test_get_post(self):
        user = backend.add_user('username','photo_url','weibo_id')
        post = Post(title='title',author_id=user['id'],pic_small='pic_small')
        db.session.add(post)
        db.session.commit()

        _post = backend.get_post(post.id)
        assert _post['title'] == 'title'

    def test_add_post(self):
        user = backend.add_user('username','photo_url','weibo_id')
        post = backend.add_post('title',user['id'],'video_url',
                pic_small='pic_small')
        
        assert post['title'] == 'title'

        post = backend.set_post(post['id'],{'title':'title2'})
        assert post['title'] == 'title2'

    def test_get_user_post(self):
        user = backend.add_user('username','photo_url','weibo_id')
        post1 = backend.add_post('title1',user['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user['id'],'video_url',
                    pic_small='pic_small')
        
        posts = backend.get_user_post(user['id'])
        assert len(posts) == 2

        count = backend.get_user_post_count(user['id'])
        assert count == 2


    def test_get_user_liked_post(self):
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        user2 = backend.add_user('username2','photo_url','weibo_id2')
        post1 = backend.add_post('title1',user1['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user1['id'],'video_url',
                    pic_small='pic_small')

        ula1 = UserLikeAsso(user_id=user2['id'],post_id=post1['id'])
        ula2 = UserLikeAsso(user_id=user2['id'],post_id=post2['id'])
        db.session.add(ula1)
        db.session.add(ula2)
        db.session.commit()

        posts = backend.get_user_liked_post(user2['id'])
        assert len(posts) == 2

        count = backend.get_user_liked_post_count(user2['id'])
        assert count == 2


    def test_add_like(self):
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        post1 = backend.add_post('title1',user1['id'],'video_url',
                    pic_small='pic_small')

        ret = backend.add_like(user1['id'],post1['id'])
        assert ret == 1

        ret = backend.del_like(user1['id'],post1['id'])
        assert ret == True

    def test_is_like_post(self):
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        post1 = backend.add_post('title1',user1['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user1['id'],'video_url',
                    pic_small='pic_small')

        backend.add_like(user1['id'],post1['id'])
        backend.add_like(user1['id'],post2['id'])

        ret = backend.is_like_post(user1['id'],[post1['id'],post2['id']])
        assert ret[post1['id']] == True


class TestActivityLogic(TestCase):

    def test_add_activity(self):
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        user2 = backend.add_user('username2','photo_url','weibo_id2')
        post1 = backend.add_post('title1',user1['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user1['id'],'video_url',
                    pic_small='pic_small')

        ac1 = {
                'post_id':post1['id'],
                'from_id':user1['id'],
                'to_id':user2['id'],
                'atype':'like'
                }
        ac2 = {
                'post_id':post1['id'],
                'from_id':user1['id'],
                'to_id':user2['id'],
                'atype':'comment'
                }

        ret = backend.add_activity(ac1)
        assert ret['to_id'] == user2['id']
        ret = backend.add_activity(ac2)

        rets = backend.get_activity_by_user(user2['id'])
        assert len(rets) == 2


class TestOtherLogic(TestCase):

    def test_new_install(self):
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        device_token = '1234567890'
        install = backend.new_install(user1['id'],device_token)
        assert install['device_token'] == device_token

        install = backend.get_install_by_user(user1['id'])

        assert install['device_token'] == device_token

        install = backend.set_install(user1['id'],{'badge':20})
        print install
        assert install['badge'] == 20

    def test_add_file_data(self):
        st = backend.add_file_data(10,'1234567890')
        st = backend.add_file_data(10,'123243435454545')
        assert len(st)  == 36

class TestCommentLogic(TestCase):

    def test_comment(self):
        user1 = backend.add_user('username1','photo_url','weibo_id1')
        user2 = backend.add_user('username2','photo_url','weibo_id2')
        post1 = backend.add_post('title1',user1['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user1['id'],'video_url',
                    pic_small='pic_small')

        
        comment1 = backend.add_comment(post1['id'],'comment1',user2['id'])
        assert comment1['post_id'] == post1['id']

        comment2 = backend.add_comment(post1['id'],'comment2',user2['id'])
        
        comments = backend.get_post_comment(post1['id'])

        assert len(comments) == 2
        
        ret = backend.get_post_comment_count(post1['id'])
        assert ret == 2

class TestTagLogic(TestCase):

    def test_tag(self):

        tag1 = Tag(name='tag1',show=True,pic_url='pic_url',
                    recommended=True)
        tag2 = Tag(name='tag2',show=True,pic_url='pic_url',
                    recommended=True)
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.commit()

        tags = backend.get_all_tags()
        assert len(tags) == 2

        tags = backend.get_recommend_tags()
        assert len(tags) == 2

        tag = backend.get_tag(tag1.id)

        assert tag['name'] == 'tag1'
        
        user = backend.add_user('username','photo_url','weibo_id')
        post1 = backend.add_post('title1',user['id'],'video_url',
                    pic_small='pic_small')
        post2 = backend.add_post('title2',user['id'],'video_url',
                    pic_small='pic_small')

        tagging1 = Tagging(taggable_type='post',taggable_id=post1['id'],
                tag_id=tag1.id)
        tagging2 = Tagging(taggable_type='post',taggable_id=post2['id'],
                tag_id=tag1.id)
        
        db.session.add(tagging1)
        db.session.add(tagging2)
        db.session.commit()

        posts = backend.get_tag_post(tag1.id)
        assert len(posts) == 2

        post_count = backend.get_tag_post_count(tag1.id)
        assert post_count == 2
        
        
class TestFeedLogic(TestCase):

    def test_get_latest_feed(self):
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
        

        ret = backend.get_latest_feed(user4['id'],limit=10,offset=0)
        assert len(ret) == 3

        backend.set_post(post3['id'],{'recommended':True})

        ret = backend.get_latest_feed(user4['id'],limit=10,offset=0)
        assert len(ret) == 4

