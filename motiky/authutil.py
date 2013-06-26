# -*- coding: utf-8 -*-

import os
import sys
import time
import hmac
import datetime
import hashlib
from hashlib import sha1,md5

import strutil

from flask import g,request,redirect,session
from flask import current_app as app

from motiky.configs import db,redis
from motiky.logic.models import User

def user_required(f):
    """必须登陆后才能访问的视图"""
    def decorator(*args,**kwargs):
        ukey = g.ukey
        if not ukey:
            return make_response('need a user',403)
        rp = redis.pipeline()
        rp.exists('USER-UKEY::%s'%ukey)
        rp.get('USER-UKEY::%s'%ukey)
        res = iter(rp.execute())
        
        if not res.next():
            # redis 中不存在 插数据库
            user = db.session.query(User).filter(User.uid == ukey).first()
            if user is None:
                res = make_response('the user does not exist',403)
                return res
            g.user_id = user.id
            rp.set('USER-UKEY::%s'%ukey,user.id)
            rp.execute()
        else:
            g.user_id = int(res.next())
        return f(*args,**kwargs)
    return decorator

def get_user_id(ukey):
    """根据ukey来获取user_id"""
    if not ukey:
        return None
    rp = redis.pipeline()
    rp.exists('USER-UKEY::%s'%ukey)
    rp.get('USER-UKEY::%s'%ukey)
    res = iter(rp.execute())

    user_id = None
    if not res.next():
        user = db.session.query(User).filter(User.uid == ukey).first()
        if user is None:
            return None
        g.user_id = user_id = user.id
        rp.set('USER-UKEY::%s'%ukey,user.id)
        rp.execute()
    else:
        g.user_id = user_id = int(res.next())
    return user_id

