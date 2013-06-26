# -*- coding: utf-8 -*-

# author: notedit <notedit@gmail.com>

import sys 
import time
import logging
from datetime import datetime

import requests

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

from motiky.schema import NewUserSchema,UpdateUserSchema,UserFollowSchema,\
                        InstallSchema,PushSchema

instance = Blueprint('user',__name__)

class UserView(MethodView):

    def get(self,user_id):
        user = backend.get_user(user_id)
        return jsonify(**user)

    def get_weibo_info(self,uid,access_token):
        if current_app.config.get('CONFIG_TYPE') == 'test':
            return {'username':'notedit',
                    'photo_url':'photo_url',
                    'signature':'signature'}

        resp = requests.get('https://api.weibo.com/2/users/show.json',
                            params={
                                'uid':uid,
                                'access_token':access_token
                                })
        _ = resp.json
        return {'username':_['screen_name'],
                'photo_url':_['avatar_large'],
                'signature':_['description']}


    def post(self):
        data = NewUserSchema().deserialize(request.json)
        print 'data',data
        try:
            user = backend.get_user_by_uid(data['uid'].encode('utf-8'))
            user = backend.set_user(user['id'],
                        {
                        'uid':data['uid'].encode('utf-8'),
                        'access_token':data['access_token'].encode('utf-8')
                        })
        except BackendError,ex:
            if ex.message == 'EmptyError':
                user = {}
            else:
                return jsonify(error='服务器开小差了')
        else:
            return jsonify(**user)

        _data = self.get_weibo_info(data['uid'],data['access_token'])
        data.update(_data)
        try:
            user = backend.add_user(
                        data['username'].encode('utf-8'),
                        data['photo_url'].encode('utf-8'),
                        data['uid'].encode('utf-8'),
                        data['signature'].encode('utf-8'),
                        data['access_token'].encode('utf-8')
                    )
        except BackendError,ex:
            return jsonify(error='add new user error')

        print 'add user',user
        user.update({'new':True})
        return jsonify(**user)

    def put(self,user_id):
        data = UpdateUserSchema().deserialize(request.json)
        try:
            user = backend.set_user(user_id,data)
        except BackendError,ex:
            raise ex
        else:
            return '',204


class InstallView(MethodView):

    def post(self):
        data = InstallSchema().deserialize(request.json)
        
        user_id = data['user_id']
        try:
            install = backend.get_install_by_user(user_id)
        except BackendError,ex:
            install = None

        if not install:
            install = backend.new_install(
                    data['user_id'],
                    data['device_token'].encode('utf-8'),
                    data['version'],
                    data['device_type'])

        return jsonify(install_id=install['id'])


class UserFollowView(MethodView):

    def post(self):
        '''关注用户'''
        data = UserFollowSchema().deserialize(request.json)
        from_id = authutil.get_user_id(g.ukey)
        for uid in data['user_ids']:
            try:
                backend.follow_user(from_id,uid)
                backend.add_activity({
                        'from_id':from_id,
                        'to_id':uid,
                        'atype':'follow'
                    })
            except BackendError,ex:
                pass

        return '',201


    def delete(self,user_id_to):
        '''取消关注'''
        user_id = authutil.get_user_id(g.ukey)
        try:
            backend.unfollow_user(user_id,user_id_to)
        except BackendError,ex:
            raise 
        return '',204


class UserIsFollowingView(MethodView):

    def get(self,user_id_to):
        user_id = authutil.get_user_id(g.ukey)
        ret = backend.is_following_user(user_id,user_id_to)
        return jsonify(is_follow=ret)


class UserFollowingView(MethodView):

    def get(self,user_id):
        try:
            page = int(request.values.get('page'))
        except:
            page = 1

        limit = 50
        offset = (page-1) * 50

        following_users = backend.get_user_following(user_id,limit=limit,
                                offset=offset)

        curr_user = backend.get_user_by_uid(g.ukey)

        fids = [u['id'] for u in following_users]
        fdict = backend.is_following_user(curr_user['id'],fids)
        for fu in following_users:
            fu['follower_count'] = backend.get_user_follower_count(fu['id'])
            fu['is_follow'] = fdict.get(fu['id']) or False
        count = backend.get_user_following_count(user_id)
        total_page = (count + 49) / 50
        return jsonify(users=following_users,page=page,total_page=total_page)


class UserFollowerView(MethodView):

    def get(self,user_id):
        try:
            page = int(request.values.get('page'))
        except:
            page = 1

        limit = 50
        offset = (page - 1) * 50
        followers = backend.get_user_follower(user_id,limit=limit,offset=offset)
        fids = [u['id'] for u in followers]

        curr_user = backend.get_user_by_uid(g.ukey)

        fdict = backend.is_following_user(curr_user['id'],fids)
        for fu in followers:
            fu['follower_count'] = backend.get_user_follower_count(fu['id'])
            fu['is_follow'] = fdict.get(fu['id']) or False
        count = backend.get_user_follower_count(user_id)
        total_page = (count + 49) / 50
        return jsonify(users=followers,page=page,total_page=total_page)

class ProfileView(MethodView):

    def get(self,user_id):
        user = backend.get_user(user_id)

        user_following_count = backend.get_user_following_count(user_id)
        user_follower_count = backend.get_user_follower_count(user_id)
        user_post_count = backend.get_user_post_count(user_id)
        user_liked_post_count = backend.get_user_liked_post_count(user_id)

        curr_user = backend.get_user_by_uid(g.ukey)

        is_follow = backend.is_following_user(curr_user['id'],user_id)
        
        pd = {
                'is_follow':is_follow,
                'following_count':user_following_count,
                'follower_count':user_follower_count,
                'post_count':user_post_count,
                'liked_post_count':user_liked_post_count
                }
        user.update(pd)
        return jsonify(**user)


instance.add_url_rule('/user',view_func=UserView.as_view('user'),
                        methods=['POST',])
instance.add_url_rule('/user/<int:user_id>',view_func=UserView.as_view('user'),
                        methods=['GET','PUT'])
instance.add_url_rule('/install',view_func=InstallView.as_view('install'),
                        methods=['POST'])
instance.add_url_rule('/user/follow',view_func=UserFollowView.as_view('user_follow'),
                        methods=['POST'])
instance.add_url_rule('/user/follow/<int:user_id_to>',view_func=UserFollowView.as_view('user_follow'),
                        methods=['DELETE'])
instance.add_url_rule('/user/isfollowing/<int:user_id>',
                        view_func=UserIsFollowingView.as_view('user_is_following'),
                        methods=['GET'])
instance.add_url_rule('/user/following/<int:user_id>',
                        view_func=UserFollowingView.as_view('user_following'),
                        methods=['GET'])
instance.add_url_rule('/user/follower/<int:user_id>',
                        view_func=UserFollowerView.as_view('user_follower'),
                        methods=['GET'])
instance.add_url_rule('/user/profile/<int:user_id>',
                        view_func=ProfileView.as_view('user_profile'),
                        methods=['GET'])

