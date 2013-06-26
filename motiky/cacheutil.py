# -*- coding: utf-8 -*-
# File: cacheutil.py

"""
一个进程内缓存的实现  应急的时候才用  并不是很安全
"""
import types
import time
import hashlib
import json

from motiky.configs import redis

LOCALCACHE_POOL={}              #本地缓存字典
LOCALCACHE_MAX_ITEM_COUNT=10000  #最大存储对象数量
LOCALCACHE_KILL_COUNT=1000       #缓存满时删除对象数量


def rcache(timeout, cachekey=None):
    """基于redis 的函数调用缓存"""
    def inter1(func):
        def inter2(*args,**kwargs):
            if cachekey is not None:
                callstr = cachekey
            else:
                params = map(lambda xx:repr(xx),args)
                for (k,v) in kwargs.items():
                    params.append('%s=%s'%(k,repr(v)))
                callstr='CALLCACHE::%s(%s)' % (func.func_name,','.join(params))
            retobj = redis.get(callstr)
            if retobj:
                return json.loads(retobj)
            retobj = func(*args,**kwargs)
            rp = redis.pipeline()
            rp.set(callstr,json.dumps(retobj)).expire(callstr,timeout).execute()
            return retobj
        return inter2
    return inter1

def delete_cache(cachekey=None):
    """用相同的参数删除rcache"""
    def inter1(func):
        def inter2(*args,**kwargs):
            if cachekey is not None:
                callstr = cachekey
            else:
                params = map(lambda xx:repr(xx),args)
                for (k,v) in kwargs.items():
                    params.append('%s=%s'%(k,repr(v)))
                callstr='CALLCACHE::%s(%s)' % (func.func_name,','.join(params))
            redis.delete(callstr)
        return inter2
    return inter1

def ugc_control_set(user_id,obj_type,obj_id,timeout):
    """
    设置UGC的时间
    可以在执行ugc操作之前先过来set 一下,如果返回True则允许下一步
    False则因为太频繁不允许ugc
    """
    assert type(user_id) == types.IntType
    assert type(timeout) == types.IntType
    q = {
            'user_id':user_id,
            'obj_type':obj_type,
            'obj_id':obj_id
            }
    _key = """UGC::%(user_id)s::%(obj_type)s::%(obj_id)s""" % q
    ret = redis.get(_key)
    if ret != None:
        return False
    else:
        redis.pipeline().set(_key,'on').expire(_key,timeout).execute()
        return True

def callcache(timeout):
    """函数的调用缓存"""
    def inter1(func):
        def inter2(*args,**kwargs):
            params=map(lambda xx:repr(xx),args)
            for (k,v) in kwargs.items():
                params.append('%s=%s'%(k,repr(v)))
            callstr='%s(%s)'%(func.__name__,','.join(params))
            try:
                cachedict=LOCALCACHE_POOL[callstr]
                if cachedict['timeout']==None:
                    return cachedict['return']
                elif cachedict['timeout']>time.time():
                    return cachedict['return']
                else:
                    del LOCALCACHE_POOL[callstr]
            except KeyError:
                pass
            retobj=func(*args,**kwargs)
            if len(LOCALCACHE_POOL)>=LOCALCACHE_MAX_ITEM_COUNT:
                clear_localcache()
            cachedict={'return':retobj,}
            if timeout:
                cachedict['timeout']=int(time.time())+timeout
            else:
                cachedict['timeout']=None
            LOCALCACHE_POOL[callstr]=cachedict
            return retobj
        return inter2
    return inter1


def clear_localcache():
    """将本地缓存清理出一块空间来"""
    for (callstr,cachedict) in LOCALCACHE_POOL.items():
        if cachedict['timeout']<time.time():
            del LOCALCACHE_POOL[callstr]    #删除已经超时的
    #need_del_left=len(LOCALCACHE_POOL)-LOCALCACHE_MAX_ITEM_COUNT
    need_del_left=len(LOCALCACHE_POOL)+LOCALCACHE_KILL_COUNT-LOCALCACHE_MAX_ITEM_COUNT
    for (callstr,cachedict) in LOCALCACHE_POOL.items():
        if cachedict['timeout']!=None:
            del LOCALCACHE_POOL[callstr]
            need_del_left-=1
            if need_del_left<=0:
                break
    return



