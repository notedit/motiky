# -*- coding: utf-8 -*-

# author: notedit <notedit@gmail.com>

import os
import sys 
import time
import uuid
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

from werkzeug import secure_filename

from motiky import authutil
from motiky.logic import backend
from motiky.coreutil import BackendError
from motiky.logic.models import User,Post,Report,Install,\
        UserFollowAsso,UserLikeAsso,Comment,Activity,Tag,Tagging,\
        CmsUser,Storage

from motiky.upyun import UpYun,md5,md5file

instance = Blueprint('admin',__name__)

upYun = UpYun('xxxxxx','xxxxxx','xxxxxx')
upYun.setApiDomain('v0.api.upyun.com')
upYun.debug = True

@instance.route('/users')
def users_list():
    page = request.values.get('page','1')
    try:
        page = int(page)
    except:
        page = 1

    _users = User.query.order_by(User.date_create.desc()).limit(20).\
                offset((page - 1) * 20).all()

    users_count = User.query.count()

    users = []
    for u in _users:
        us = u.json
        users.append(us)

    total_page = (users_count + 19) / 20
    
    return render_template('user_list.html',users=users,page=page,total_page=total_page)


@instance.route('/posts')
def post_list():
    page = request.values.get('page','1')
    try:
        page = int(page)
    except:
        page = 1

    _posts = Post.query.order_by(Post.date_create.desc()).limit(20).\
                offset((page - 1) * 20).all()
                
    posts_count = Post.query.count()

    posts = []
    for po in _posts:
        pos = po.json
        user = po.user.json
        pos['user'] = user
        posts.append(pos)

    total_page = (posts_count + 19) / 20
    
    return render_template('post_list.html',posts=posts,count=posts_count,
                                            page=page,total_page=total_page)

@instance.route('/post/<int:post_id>/recommend')
def post_recommend(post_id):
    post = Post.query.get(post_id)
    post.recommended = True
    db.session.commit()
    return redirect('/admin/posts')

@instance.route('/post/<int:post_id>/not_recommend')
def post_recommend(post_id):
    post = Post.query.get(post_id)
    post.recommended = False
    db.session.commit()
    return redirect('/admin/posts')

@instance.route('/post/<int:post_id>/show')
def post_recommend(post_id):
    post = Post.query.get(post_id)
    post.show = True
    db.session.commit()
    return redirect('/admin/posts')

@instance.route('/post/<int:post_id>/hide')
def post_recommend(post_id):
    post = Post.query.get(post_id)
    post.show = False
    db.session.commit()
    return redirect('/admin/posts')

@instance.route('/tags')
def tag_list():
    page = request.values.get('page','1')
    try:
        page = int(page)
    except:
        page = 1

    _tags = Tag.query.order_by(Post.date_create.desc()).limit(20).\
                offset((page - 1) * 20).all()
                
    tags_count = Tag.query.count()

    tags = []
    for t in _tags:
        t = t.json
        tags.append(t)

    total_page = (tags_count + 19) / 20
    
    return render_template('tag_list.html',tags=tags,
                                            page=page,total_page=total_page)

@instance.route('/add_tag')
def add_tag():
    if request.method == 'GET':
        return render_template('add_tag.html')

    name = request.values.get('name')
    pic_url = request.values.get('pic_url')
    order_seq = request.values.get('order_seq')
    show = request.values.get('show') == 'true' or False
    recommended = request.values.get('recommended') == 'true' or False

    tag = Tag()
    tag.name = name
    tag.pic_url = pic_url
    tag.order_seq = order_seq
    tag.show = show
    tag.recommended = recommended

    try:
        db.session.add(tag)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return redirect('/admin/tags')

@instance.route('/tag/<int:tag_id>/edit')
def edit_tag(tag_id):
    tag = Tag.query.get(tag_id)

    if request.method == 'GET':
        return render_template('edit_tag.html',tag=tag.json)

    name = request.values.get('name')
    pic_url = request.values.get('pic_url')
    order_seq = request.values.get('order_seq')
    show = request.values.get('show') == 'true' or False
    recommended = request.values.get('recommended') == 'true' or False

    tag.name = name
    tag.pic_url = pic_url
    tag.order_seq = order_seq
    tag.show = show
    tag.recommended = recommended

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return redirect('/admin/tags')


@instance.route('/upload',methods=['POST','GET'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html',file_name='')

    pic_file = request.files.get('upload')
    fname = secure_filename(pic_file.filename)
    extn = os.path.splitext(fname)[1]
    cname = '/' + str(uuid.uuid4()) + str(extn)
    pic_data = strutil.read_data(pic_file)
    upYun.writeFile(cname,pic_data)
    
    cname = upyun_prefix + cname
    return render_template('upload.html',file_name=cname)



