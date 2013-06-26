# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-04-10

import os
import types
import traceback
from datetime import datetime

from flask import current_app

from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,Tag,Activity,UserFollowAsso

from motiky.configs import db,DefaultConfig


NEW_FEED_SQL = """
        SELECT id FROM answer WHERE show=true AND date_create > %(last_update_time)s 
        AND (%(following_limit)s) LIMIT 1
        """

GET_LATEST_FEED_SQL = """
        SELECT id,title,pic_small,pic_big,video_url,author_id,show,recommended,play_count,
        date_create,date_update,date_publish FROM post WHERE date_create < %(now)s AND show=true 
        AND (%(following_limit)s) ORDER BY date_create DESC 
        LIMIT %(limit)s OFFSET %(offset)s
        """
        
VALUE_LIST = ['id','title','pic_small','pic_big','video_url','author_id',
                'show','recommended','play_count','date_create','date_update',
                'date_publish']

def _get_following_user(user_id):
    fu = UserFollowAsso.query.filter(UserFollowAsso.user_id == user_id).all()
    if fu:
        fuids = [u.user_id_to for u in fu if u]
    else:
        fuids = []
    return fuids

@register('get_new_feed')
def get_new_feed(user_id,last_update_time):

    fus = _get_following_user(user_id)
    fus.extend([user_id])
    fus = set(fus)

    following_limit = []
    if fus:
        following_limit.append('author_id IN (%s)' % ','.join([repr(uid) for uid in fus]))
    else:
        following_limit.append('1=1')

    following_limit.append('recommended = true')

    following_limit = ' OR '.join(following_limit)

    sql = NEW_FEED_SQL % {'following_limit':following_limit,'last_update_time':repr(str(last_update_time))}

    res = db.session.execute(sql).fetchall()
    return True if len(res) else False

@register('get_latest_feed')
def get_latest_feed(user_id,limit,offset):
    
    qd = {
            'limit':repr(limit),
            'offset':repr(offset)
            }
    
    fus = _get_following_user(user_id)
    fus.extend([user_id])
    fus = set(fus)
    
    following_limit = []
    if fus:
        following_limit.append('author_id IN (%s)' % ','.join([repr(uid) for uid in fus]))
    else:
        following_limit.append('1=1')

    following_limit.append('recommended = true')

    following_limit = ' OR '.join(following_limit)

    _now = repr(str(datetime.now()))

    qd.update({'following_limit':following_limit,'now':_now})
    sql = GET_LATEST_FEED_SQL % qd

    print sql

    video_url_prefix = '/' if not current_app else current_app.config.get('VIDEO_URL_PREFIX')

    res = db.session.execute(sql).fetchall()
    ress = []
    for re in res:
        _dict = dict(zip(VALUE_LIST,re))
        _dict.update({
            'date_create':_dict['date_create'].strftime('%Y-%m-%d %H:%M:%S'),
            'date_update':_dict['date_update'].strftime('%Y-%m-%d %H:%M:%S'),
            'date_publish':_dict['date_publish'].strftime('%Y-%m-%d %H:%M:%S'),
            'video_url':os.path.join(video_url_prefix,_dict['video_url'] or ''),
            'pic_small':os.path.join(video_url_prefix,_dict['pic_small'] or ''),
            })
        ress.append(_dict)
    return ress
