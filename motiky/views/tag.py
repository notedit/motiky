# -*- coding: utf-8 -*-
# author: notedit <notedit@gmail.com>
# date: 2013-04-16

import sys 
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
from motiky.logic import backend
from motiky.coreutil import BackendError
from motiky.configs import rq

instance = Blueprint('tag',__name__)

class TagView(MethodView):

    def get(self,tag_id):
        try:
            page = int(request.values.get('page'))
        except:
            page = 1

        limit = 10
        offset = (page - 1) * 50

        tag = backend.get_tag(tag_id)
        posts = backend.get_tag_post(tag_id,limit=limit,offset=offset)
        count = backend.get_tag_post_count(tag_id)

        for post in posts:
            try:
                user = backend.get_user(post['author_id'])
                post['user'] = user
            except BackendError,ex:
                continue

        return jsonify(tag=tag,posts=posts,count=count,page=page)

class TagsView(MethodView):

    def get(self):
        tags = backend.get_recommend_tags()
        return jsonify(results=tags)

instance.add_url_rule('/tag/<int:tag_id>',view_func=TagView.as_view('tag'),
                    methods=['GET',])
instance.add_url_rule('/tags',view_func=TagsView.as_view('tags'),
                    methods=['GET',])






