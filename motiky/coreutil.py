# -*- coding: utf-8 -*- 

import os
import sys
import time
import logging
import inspect
import traceback



backend_mapping = {}
def register(funcname=None):
    global backend_mapping 
    def inter1(func,funcname=None):
        funcname = funcname if funcname else func.__name__
        if not backend_mapping.has_key(funcname):
            backend_mapping[funcname] =func
        else:
            raise KeyError('%s:funcname declare more than once '%repr(funcname))
        def inter2(*args,**kwargs):
            return func(*args,**kwargs)
        setattr(inter2,'argspec',inspect.getargspec(func))
        return inter2
    return lambda func:inter1(func,funcname)

def assert_error(expr,msg,detail=''):
    if not expr:
        if not detail:
            detail = msg
        raise BackendError(msg,detail)

class BackendError(Exception):
    def __init__(self,message,detail):
        self.message = message
        self.detail = detail
        
    def __str__(self):
        return 'BackendError(%s,%s)' % (self.message,self.detail)

    def __repr__(self):
        return 'BackendError(%s,%s)' %(self.message,self.detail)


class Backend(object):
    '''去掉一些后端不需要导出的方法'''
    def __init__(self,func_mapping):
        self.func_mapping = func_mapping

    def __getattr__(self,attr_name):
        if self.func_mapping.has_key(attr_name):
            func = lambda *args,**kwargs: self.__call__(attr_name,*args,**kwargs)
            func.__name__ = 'backend.' + attr_name
            return func
        else:
            raise AttributeError('backend does not have %s attibute'%attr_name)


    def __call__(self,funcname,*args,**kwargs):
        try:
            return self.func_mapping[funcname](*args,**kwargs)
        except BackendError,ex:
            print ex.detail
            raise ex 
        except Exception,ex:
            excstr = traceback.format_exc()
            print excstr
            raise BackendError('BackendError',excstr)





