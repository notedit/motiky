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

from motiky.schema import NewCommentSchema

instance = Blueprint('comment',__name__)


class CommentView(MethodView):

    def post(self):
        data = NewCommentSchema().deserialize(request.json)
        
        user = backend.get_user(data['author_id'])

        post = backend.get_post(data['post_id'])

        if user['uid'] != g.ukey:
            return jsonify(error='not the user')
        
        try:
            comment = backend.add_comment(
                    data['post_id'],
                    data['content'].encode('utf-8'),
                    data['author_id']
                    )
        except BackendError,ex:
            raise

        if post['author_id'] != data['author_id']:
            try:
                backend.add_activity({
                    'post_id':data['post_id'],
                    'comment_id':comment['id'],
                    'from_id':data['author_id'],
                    'to_id':post['author_id'],
                    'atype':'comment'
                    })
            except BackendError,ex:
                pass

        return jsonify(**comment)

    def delete(self,comment_id):
        comment = backend.get_comment(comment_id)
        try:
            backend.set_comment(comment_id,{'show':False})
        except BackendError,ex:
            abort(501)
        else:
            return '',204


class PostCommentsView(MethodView):

    def get(self,post_id):
        try:
            page = int(request.values.get('page','1'))
        except:
            page = 1

        limit = 20
        offset = (page-1)*limit

        comments = backend.get_post_comment(post_id,
                limit=limit,offset=offset)

        for comment in comments:
            user = backend.get_user(comment['author_id'])
            comment['user'] = user

        count = backend.get_post_comment_count(post_id)
        total_page = (count + limit -1 ) / limit
        return jsonify(comments=comments,page=page,total_page=total_page)


instance.add_url_rule('/comment',view_func=CommentView.as_view('comment'),
                        methods=['POST'])
instance.add_url_rule('/comment/<int:comment_id>',
                        view_func=CommentView.as_view('comment_delete'),
                        methods=['DELETE'])
instance.add_url_rule('/post/<int:post_id>/comment',
                        view_func=PostCommentsView.as_view('post_comment'),
                        methods=['GET'])





