# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-04-15

import types
import traceback


from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,Comment

from motiky.configs import db,redis


@register('add_comment')
def add_comment(post_id,content,author_id):
    assert_error(type(post_id) == types.IntType,'ParamError')
    assert_error(type(author_id) == types.IntType,'ParamError')
    assert_error(type(content) == types.StringType,'ParamError')

    qd = {
            'post_id':post_id,
            'content':content,
            'author_id':author_id
            }
    co = Comment(**qd)
    try:
        db.session.add(co)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    return co.json

@register('set_comment')
def set_comment(comment_id,dinfo):
    keys_set = ('post_id','author_id','content','show','date_create')
    if not set(dinfo.keys()).issubset(keys_set):
        raise BackendError('ParamError','更新的字段不允许')
    comment = Comment.query.get(comment_id)
    for key,value in dinfo.items():
        if value is not None:
            setattr(comment,key,value)
    try:
        db.session.commit()
    except Exception,ex:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    return comment.json

@register('get_comment')
def get_comment(comment_id):
    assert_error(type(comment_id) == types.IntType,'ParamError')
    comm = Comment.query.get(comment_id)
    return comm.json

@register('get_post_comment')
def get_post_comment(post_id,limit=50,offset=0,show=True):
    assert_error(type(post_id) == types.IntType,'ParamError')
    _ans = [Comment.show == True,] if show else []
    _ans.append(Comment.post_id == post_id)
    q = reduce(db.and_,_ans)
    comms = Comment.query.filter(q).order_by(Comment.date_create.desc()).\
            limit(limit).offset(offset).all()
    return [c.json for c in comms]

@register('get_post_comment_count')
def get_post_comment_count(post_id,show=True):
    _ans = [Comment.show == True,] if show else []
    _ans.append(Comment.post_id == post_id)
    q = reduce(db.and_,_ans)
    count = Comment.query.filter(q).count()
    return count

@register('add_comment_count')
def add_comment_count(post_id,step=1):
    count_key = 'POST::COMMENT_COUNT::%s' % str(post_id)
    if redis.exists(count_key):
        rp = redis.pipeline()
        rp.incr(count_key).expire(count_key,24*5*3600).execute()



