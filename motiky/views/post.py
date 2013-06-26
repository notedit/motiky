# -*- coding: utf-8 -*-

# author: notedit <notedit@gmail.com>

import os
import sys
import md5
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
from motiky import strutil
from motiky.logic import backend
from motiky.coreutil import BackendError

from motiky.upyun import UpYun,md5,md5file

from motiky.schema import NewPostSchema,UpdatePostSchema,\
                        PostLikeSchema,PostUnlikeSchema

instance = Blueprint('post',__name__)

upYun = UpYun('xxxxxxxx','xxxxxxxxxx','xxxxxxxxx')
upYun.setApiDomain('v0.api.upyun.com')
upYun.debug = True

def save_file(file_data,ftype):
    file_md5 = md5(file_data)
    file_size = len(file_data)
    file_id = backend.add_file_data(file_size,file_md5)
    extname = 'mp4' if ftype == 'video' else 'jpg'
    file_url = '%s.%s' % (file_id,extname)
    if current_app.config.get('CONFIG_TYPE') == 'production':
        upYun.writeFile('/'+file_url,file_data)
    else:
        writeFile('/storage/' + file_url,file_data)
    return file_id,file_url


def writeFile(file_url,file_data):
    dirname = os.path.dirname(file_url)
    if not os.path.exists(dirname):
        os.makedirs(dirname,0777)

    with open(file_url,'wb') as f:
        f.write(file_data)
        f.flush()

class PostView(MethodView):

    def get(self,post_id):
        post = backend.get_post(post_id)
        curr_user = backend.get_user_by_uid(g.ukey)
        post['is_like'] = backend.is_like_post(curr_user['id'],post['id'])
        post['like_count'] = backend.get_post_liked_count(post_id)
        post['comment_count'] = backend.get_post_comment_count(post_id)
        return jsonify(**post)

    def post(self):
        _data = {
                'author_id':request.values.get('author_id'),
                'title':request.values.get('title'),
                }
        data = NewPostSchema().deserialize(_data)
        
        user = backend.get_user(data['author_id'])
        
        if user['uid'] != g.ukey:
            return jsonify(error='not the user')

        # video_file
        video_file = request.files.get('video_file')
        video_data = strutil.read_data(video_file)
        video_id,video_url = save_file(video_data,'video')

        # pic_file
        pic_file = request.files.get('pic_file')
        pic_data = strutil.read_data(pic_file)
        pic_id,pic_url = save_file(pic_data,'pic')

        data['title'] = data['title'].encode('utf-8') if data['title'] else ''
        try:
            post = backend.add_post(
                    data['title'],
                    data['author_id'],
                    video_url,
                    pic_small=pic_url
                    )
        except BackendError,ex:
            raise

        tags = strutil.extract_tags(data['title'])

        if tags:
            backend.add_post_tag(post['id'],tags)

        return jsonify(**post)

    def put(self,post_id):
        data = UpdatePostSchema().deserialize(request.json)
        try:
            backend.set_post(post_id,data)
        except BackendError,ex:
            abort(501)
        else:
            return '',204

    def delete(self,post_id):
        post = backend.get_post(post_id)
        curr_id = authutil.get_user_id(g.ukey)
        if post['author_id'] != curr_id:
            return jsonify(error='forbid')
        try:
            backend.set_post(post_id,{'show':'deleted_by_user'})
        except BackendError,ex:
            abort(501)
        else:
            return '',204


class PostListView(MethodView):

    def get(self):
        try:
            page = int(request.values.get('page','1'))
        except:
            page = 1

        limit = 20
        offset = (page-1)*limit

        posts = backend.get_latest_post(limit=limit,offset=offset)
        count = backend.get_post_count()

        for post in posts:
            post['like_count'] = backend.get_post_liked_count(post['id'])
            post['comment_count'] = backend.get_post_comment_count(post['id'])
        
        total_page = (count + limit -1 ) / limit
        return jsonify(posts=posts,page=page,total_page=total_page)


class UserPostView(MethodView):

    def get(self,user_id):
        try:
            page = int(request.values.get('page','1'))
        except:
            page = 1

        limit = 20
        offset = (page-1) * limit
        
        curr_user = backend.get_user_by_uid(g.ukey)
        user_posts = backend.get_user_post(user_id,limit=limit,offset=offset)

        liked_post_ids = [p['id'] for p in user_posts];
        liked_dict = backend.is_like_post(curr_user['id'],liked_post_ids)
        for up in user_posts:
            up['is_like'] = liked_dict.get(up['id']) or False
            up['like_count'] = backend.get_post_liked_count(up['id'])
            up['comment_count'] = backend.get_post_comment_count(up['id'])
        


        count = backend.get_user_post_count(user_id)
        total_page = (count + limit - 1) / limit

        return jsonify(posts=user_posts,page=page,total_page=total_page)

class UserLikedPostView(MethodView):

    def get(self,user_id):
        try:
            page = int(request.values.get('page'))
        except:
            page = 1

        limit = 20
        offset = (page-1) * limit

        liked_posts = backend.get_user_liked_post(user_id,limit=limit,offset=offset)
        for p in liked_posts:
            p['is_like'] = True
            p['like_count'] = backend.get_post_liked_count(p['id'])
            p['comment_count'] = backend.get_post_comment_count(p['id'])
        

        count = backend.get_user_liked_post_count(user_id)
        total_page = (count + limit -1) / limit
        
        return jsonify(posts=liked_posts,page=page,total_page=total_page)

class PostLikeView(MethodView):

    def post(self):
        data = PostLikeSchema().deserialize(request.json)
        try:
            ret = backend.add_like(data['user_id'],data['post_id'])
        except BackendError,ex:
            return jsonify(error='can not add like')

        try:
            post = backend.get_post(data['post_id'])
            backend.add_activity({
                    'post_id':data['post_id'],
                    'from_id':data['user_id'],
                    'to_id':post['author_id'],
                    'atype':'like'
                })
        except BackendError,ex:
            pass

        liked_count = backend.get_post_liked_count(data['post_id'])

        return jsonify(like_count=liked_count)

class PostUnlikeView(MethodView):

    def post(self):
        data = PostUnlikeSchema().deserialize(request.json)
        try:
            ret = backend.del_like(data['user_id'],data['post_id'])
        except BackendError,ex:
            raise 

        liked_count = backend.get_post_liked_count(data['post_id'])

        return jsonify(like_count=liked_count)


instance.add_url_rule('/post',view_func=PostView.as_view('post'),
                        methods=['POST'])
instance.add_url_rule('/post/<int:post_id>',view_func=PostView.as_view('post'),
                        methods=['GET','PUT','DELETE'])
instance.add_url_rule('/posts',view_func=PostListView.as_view('posts'),
                        methods=['GET'])
instance.add_url_rule('/posts/user/<int:user_id>',
                        view_func=UserPostView.as_view('user_post'),
                        methods=['GET',])
instance.add_url_rule('/posts/user/<int:user_id>/liked',
                        view_func=UserLikedPostView.as_view('user_liked_post'),
                        methods=['GET',])
instance.add_url_rule('/post/like',
                        view_func=PostLikeView.as_view('post_like'),
                        methods=['POST',])
instance.add_url_rule('/post/unlike',
                        view_func=PostUnlikeView.as_view('post_unlike'),
                        methods=['POST',])






