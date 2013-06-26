# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-02-01

import types
import traceback

from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,Install,Storage

from motiky.configs import db


@register('get_install_by_user')
def get_install_by_user(user_id):
    _in = Install.query.filter(Install.user_id == user_id).first()
    if _in is None:
        raise BackendError('EmptyError','install do not exit')
    return _in.json

@register('new_install')
def new_insall(user_id,device_token,version='',device_type=''):
    assert_error(type(user_id) == types.IntType,'ParamError')
    assert_error(type(device_token) == types.StringType,'ParamError')
    
    install = Install(user_id=user_id,
                    device_token=device_token,
                    version=version,
                    device_type=device_type)

    try:
        db.session.add(install)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    return install.json

@register('set_install')
def set_install(user_id,idict):
    install = Install.query.filter(Install.user_id == user_id).first()
    if install is None:
        raise BackendError('EmptyError','install does not exist')
    for k,v in idict.items():
        if v:
            setattr(install,k,v)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    else:
        return install.json

@register('add_file_data')
def add_file_data(file_size,file_md5):
    st = Storage(file_size=file_size,file_md5=file_md5)
    try:
        db.session.add(st)
        db.session.commit()
    except:
        db.session.rollback()
        raise BackendError('InternalError',traceback.format_exc())
    return st.id

