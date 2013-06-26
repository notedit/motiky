# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-01-30

import types
import traceback

from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,UserLikeAsso,UserPlayAsso

from motiky.configs import db


@register('get_post')
def get_post(post_id):
    post = Post.query.get(post_id)
    return post.json

@register('add_post')
def add_post(title,author_id,video_url,pic_small='',pic_big='',show=True,recommended=False):
    assert_error(type(title) == types.StringType,'ParamError')
    assert_error(type(author_id) == types.IntType,'ParamError')
    assert_error(type(video_url) == types.StringType,'ParamError')

    qd = {
            'title':title,
            'author_id':author_id,
            'video_url':video_url,
            'pic_small':pic_small,
            'pic_big':pic_big,
            'show':show,
            'recommended':recommended,
            }
    try:
        p = Post(**qd)
        db.session.add(p)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    return p.json



@register('set_post')
def set_post(post_id,pdict):
    fd_list = ('title','pic_small','pic_big','author_id','show',
                'recommended','date_create','date_update','date_publish')
    cset = set(pdict.keys())
    if not cset.issubset(fd_list):
        raise BackendError('ParamError','更新的字段不允许')
    post = Post.query.get(post_id)
    for k,v in pdict.items():
        if v is not None:
            setattr(post,k,v)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise 

    return post.json


@register('get_latest_post')
def get_latest_post(offset=0,limit=50):
    posts = Post.query.filter(Post.show == True).order_by(Post.date_create.desc()).\
            limit(limit).offset(offset).all()

    _posts = []
    for p in posts:
        _u = p.user.json
        _p = p.json
        _p.update({'user':_u})
        _posts.append(_p)

    return _posts


@register('get_post_count')
def get_post_count():
    count = Post.query.filter(Post.show == True).count()
    return count

@register('get_hot_post')
def get_hot_post(offset=0,limit=50):
    posts = Post.query.filter(Post.show == True).order_by(Post.visite_count.desc()).\
            limit(limit).offset(offset).all()

    _posts = []
    for p in posts:
        _u = p.user.json
        _p = p.json
        _p.update({'user':_u})
        _posts.append(_p)

    return _posts

@register('get_user_post')
def get_user_post(user_id,offset=0,limit=20):
    assert_error(offset >= 0,'ParamError')
    posts = Post.query.filter(Post.author_id == user_id).\
                order_by(Post.date_create.desc()).\
                limit(limit).offset(offset).all()

    _posts = []
    for p in posts:
        _u = p.user.json
        _p = p.json
        _p.update({'user':_u})
        _posts.append(_p)

    return _posts

@register('get_user_post_count')
def get_user_post_count(user_id):
    count = Post.query.filter(Post.author_id == user_id).count()
    return count


@register('get_user_liked_post')
def get_user_liked_post(user_id,offset=0,limit=20):
    assert_error(offset >= 0,'ParamError')
    posts = Post.query.join(UserLikeAsso,Post.id == UserLikeAsso.post_id).\
            filter(UserLikeAsso.user_id == user_id).\
            order_by(UserLikeAsso.date_create.desc()).\
            limit(limit).offset(offset).all()

    _posts = []
    for p in posts:
        _u = p.user.json
        _p = p.json
        _p.update({'user':_u})
        _posts.append(_p)

    return _posts

@register('get_user_liked_post_count')
def get_user_liked_post_count(user_id):
    count = Post.query.join(UserLikeAsso,Post.id == UserLikeAsso.post_id).\
            filter(UserLikeAsso.user_id == user_id).count()
    return count

@register('get_post_liked_count')
def get_post_liked_count(post_id):
    count = UserLikeAsso.query.filter(UserLikeAsso.post_id == post_id).count()
    return count

@register('add_like')
def add_like(user_id,post_id):
    ula = UserLikeAsso()
    ula.user_id = user_id
    ula.post_id = post_id
    try:
        db.session.add(ula)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    else:
        return ula.id

@register('del_like')
def del_like(user_id,post_id):
    assert_error(all([type(x) == types.IntType for x in [user_id,post_id]]),
                    'ParamError')
    ula = UserLikeAsso.query.filter(UserLikeAsso.user_id == user_id).\
            filter(UserLikeAsso.post_id == post_id).first()
    if ula is None:
        return
    try:
        db.session.delete(ula)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    else:
        return True


@register('add_play')
def add_play(user_id,post_id):
    assert_error(all([type(x) for x in [user_id,post_id]]),'ParamError')
    ura = UserPlayAsso()
    ura.user_id = user_id
    ura.post_id = post_id

    try:
        db.session.add(ura)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())

@register('add_play_count')
def add_play_count(post_id,count=1):
    post = Post.query.get(post_id)
    post.play_count += count
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    else:
        return post.json

@register('is_like_post')
def is_like_post(uid,post_id):
    if type(post_id) == types.IntType:
        _count = db.session.query(UserLikeAsso.id).\
                filter(db.and_(UserLikeAsso.user_id == uid,
                    UserLikeAsso.post_id == post_id)).count()
        return True if _count > 0 else False
    elif type(post_id) == types.ListType:
        liked_post_ids = db.session.query(UserLikeAsso.post_id).\
                filter(db.and_(UserLikeAsso.user_id == uid,
                    UserLikeAsso.post_id.in_(post_id))).all()
        liked_post_ids = [p[0] for p in liked_post_ids]
        ret_list = [(ret,ret in liked_post_ids) for ret in post_id]
        return dict(ret_list)

