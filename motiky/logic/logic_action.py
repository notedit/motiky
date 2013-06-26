# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-01-30

import types
import traceback

from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,Action

from motiky.configs import db



@register('add_action')
def add_action(ainfo={}):
    action = Action(**ainfo)
    try:
        db.session.add(action)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    else:
        return action.json


# add some other



