# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-01-30

import types
import traceback


from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,UserFollowAsso

from motiky.configs import db

@register('get_user')
def get_user(user_id):
    multi = False
    if type(user_id) == types.ListType:
        assert_error(all([type(u) == types.IntType for u in user_id]),'ParamError')
        multi = True
    else:
        assert_error(type(user_id) == types.IntType,'ParamError')
        user_id = user_id,

    users = User.query.filter(User.id.in_(user_id)).all()
    if not users:
        raise BackendError('EmptyError','用户不存在')

    if multi:
        return [u.json for u in users]
    else:
        return users[0].json

@register('get_user_by_username')
def get_user_by_username(username):
    user = User.query.filter(User.username == username).first()
    return user.json if user else {}

@register('get_user_by_email')
def get_user_by_email(email):
    user = User.query.filter(User.email == email).first()
    return user.json if user else {}

@register('is_username_exist')
def is_username_exist(username):
    assert_error(type(username) == types.StringType,'ParamError')
    return True if _check_username(username) else False

@register('is_email_exist')
def is_email_exist(email):
    assert_error(type(email) == types.StringType,'ParamError')
    return True if _check_email(email) else False

def _check_username(username):
    u = User.query.filter(db.func.lower(User.username) == username).first()
    return u

def _check_email(email):
    u = User.query.filter(User.email == email).first()
    return u


@register('add_user')
def add_user(username,photo_url,uid,signature='',access_token=''):
    assert_error(type(username)==types.StringType,'ParamError','用户昵称应该为字符串')
    assert_error(photo_url == None or type(photo_url) == types.StringType,'ParamError')
    assert_error(type(uid) == types.StringType,'ParamError')

    qd = {
            'username':username,
            'photo_url':photo_url or '',
            'uid':uid,
            'signature':signature,
            'access_token':access_token
            }

    try:
        user = User(**qd)
        db.session.add(user)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())

    return user.json

@register('set_user')
def set_user(user_id,info_d):
    assert_error(type(user_id) == types.IntType,'ParamError')
    user = User.query.get(user_id)
    try:
        for k,v in info_d.items():
            if v is not None:
                setattr(user,k,v)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return user.json

@register('get_user_by_uid')
def get_user_by_uid(uid):
    assert_error(type(uid) in (types.StringType,types.ListType),'ParamError')
    multi = False
    if type(uid) == types.ListType:
        multi = True
    else:
        uid = uid,

    users = User.query.filter(User.uid.in_(uid)).all()
    if len(users) == 0:
        raise BackendError('EmptyError','用户不存在')

    if multi:
        return [u.json for u in users]
    else:
        return users[0].json


@register('follow_user')
def follow_user(fid,tid):
    assert_error(all([type(_id) == types.IntType for _id in [fid,tid]]),'ParamError')
    try:
        asso = UserFollowAsso(user_id=fid,user_id_to=tid)
        db.session.add(asso)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return asso.id

@register('unfollow_user')
def unfollow_user(fid,tid):
    assert_error(all([type(_id) == types.IntType for _id in [fid,tid]]),'ParamError')
    asso = UserFollowAsso.query.filter(db.and_(UserFollowAsso.user_id==fid,UserFollowAsso.user_id_to==tid)).\
            first()
    if asso is None:
        return
    try:
        db.session.delete(asso)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    else:
        return True

@register('is_following_user')
def is_following_user(uid,uid_to):
    if type(uid_to) == types.IntType:
        _count = db.session.query(UserFollowAsso.id).\
                filter(db.and_(UserFollowAsso.user_id == uid,UserFollowAsso.user_id_to == uid_to)).count()
        return True if _count > 0 else False
    elif type(uid_to) == types.ListType:
        follow_uids = db.session.query(UserFollowAsso.user_id_to).\
                filter(db.and_(UserFollowAsso.user_id == uid,UserFollowAsso.user_id_to.in_(uid_to))).all()
        follow_uids = [u[0] for u in follow_uids]
        ret_list = [(ret,ret in follow_uids) for ret in uid_to]
        return dict(ret_list)

@register('get_user_following')
def get_user_following(user_id,limit=50,offset=0):
    assert_error(type(user_id) == types.IntType,'ParamError')
    follows = User.query.join(UserFollowAsso,User.id == UserFollowAsso.user_id_to).\
            filter(UserFollowAsso.user_id == user_id).limit(limit).offset(offset).all()
    return [u.json for u in follows]

@register('get_user_following_count')
def get_user_following_count(user_id):
    _count = UserFollowAsso.query.filter(UserFollowAsso.user_id == user_id).count()
    return _count

@register('get_user_follower')
def get_user_follower(user_id,limit=50,offset=0):
    assert_error(type(user_id) == types.IntType,'ParamError')
    follows = User.query.join(UserFollowAsso,User.id == UserFollowAsso.user_id).\
            filter(UserFollowAsso.user_id_to == user_id).limit(limit).offset(offset).all()
    return [u.json for u in follows]

@register('get_user_follower_count')
def get_user_follower_count(user_id):
    _count = UserFollowAsso.query.filter(UserFollowAsso.user_id_to == user_id).count()
    return _count





