# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-04-10

import types
import traceback

from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,Tag,Activity

from motiky.configs import db

@register('add_activity')
def add_activity(ainfo):
    act = Activity(**ainfo)
    try:
        db.session.add(act)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    else:
        return act.json

@register('get_new_activity_count')
def get_new_activity_count(user_id,last_update_time):
    assert_error(type(user_id) == types.IntType,'ParamError')
    count = Activity.query.filter(Activity.to_id == user_id).\
            filter(Activity.date_create > last_update_time).count()
    return count

@register('get_activity_by_user')
def get_activity_by_user(user_id,limit=30,offset=0):
    assert_error(type(user_id) == types.IntType,'ParamError')
    activitys = Activity.query.filter(Activity.to_id == user_id).\
            order_by(db.desc(Activity.date_create)).limit(limit).offset(offset).all()
    return [a.json for a in activitys]



