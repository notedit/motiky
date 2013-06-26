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
                UserFollowAsso,Comment,Activity,Action

from motiky.logic import backend

from motiky.configs import db,redis

class TestUser(TestCase):


    def test_user_view(self):
        
        # post
        headers = self.generate_header('weibo_id1')
        data = {'uid':'weibo_id1',
                'access_token':'1111111111'}
        resp = self.client.post('/user',data=json.dumps(data),
                headers=headers,content_type='application/json')
        print resp.data
        _data = json.loads(resp.data)
        assert resp.status_code == 200
        assert _data['uid'] == 'weibo_id1'
        assert _data['access_token'] == '1111111111'

        # get
        resp = self.client.get('/user/%d'%_data['id'],headers=headers)
        data_get = json.loads(resp.data)
        assert data_get['uid'] == 'weibo_id1'

        # put
        put_in = {'photo_url':'put_url','date_upate':str(datetime.now())}
        resp = self.client.put('/user/%d'%_data['id'],
                                data=json.dumps(put_in),headers=headers,
                                content_type='application/json')
        print resp.data
        assert resp.status_code == 204

    def test_install(self):
        user1 = backend.add_user('username01','photo_url01','weibo_id01')
        device_token = 'device_token'
        
        headers = self.generate_header('weibo_id01')
        
        data = {
                'device_type':'ios',
                'device_token':device_token,
                'version':'1.1.10',
                'user_id':user1['id']
                }

        resp = self.client.post('/install',data=json.dumps(data),
                                headers=headers,content_type='application/json')

        _data = json.loads(resp.data)
        install_id = _data['install_id']
        
        install = Install.query.filter(Install.user_id == user1['id']).first()
        assert install is not None
        assert install.device_token.encode('utf-8') == device_token

    def test_user_follow(self):
        headers = self.generate_header('weibo_id01')
        pass




