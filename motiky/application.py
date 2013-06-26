# -*- coding: utf-8 -*-


import os
import logging
import hmac

from flask import g
from flask import Flask
from flask import request
from flask import make_response
from flask import session

from motiky import configs
from motiky.configs import db,cache,mail,redis

from motiky import logic
from motiky import authutil
from motiky.logic import backend
from motiky.coreutil import BackendError

from motiky.views import user,post,tag,feed,\
        activity,comment

# add some other view

__all__ = ['create_app']


DEFAULT_APP_NAME = 'motiky'


def create_app(config=None,app_name=None):
    
    if app_name is None:
        app_name = DEFAULT_APP_NAME
    
    app = Flask(app_name)

    configure_app(app,config)
    configure_db(app)
    configure_blueprints(app)
    configure_cache(app)
    configure_handler(app)
    return app

def configure_app(app,config):
    app.config.from_object(configs.DefaultConfig())

    if config is not None:
        app.config.from_object(config)

    app.config.from_envvar('APP_CONFIG',silent=True)

def configure_db(app):
    db.init_app(app)

def configure_cache(app):
    redis.init_app(app)

def configure_handler(app):

    @app.before_request
    def authorize():
        print request.headers
        if request.path.startswith('/admin'):
            return

        token = request.headers.get('X-MOTIKY-TOKEN') or ''
        tokens = token.split('|')
        if len(tokens) != 3:
            print 'unvalid request'
            response = make_response('unvalid request',403)
            return response

        ukey,_time,signature = tokens
        print ukey,_time,signature
        sign = hmac.new(app.config.get('APPLICATION_SECRET'),ukey+_time).hexdigest()
        if sign != signature:
            print 'sian != signature  unvalid request'
            response = make_response('unvalid request',403)
            return response
        g.ukey = ukey


def configure_blueprints(app):
    app.register_blueprint(user.instance,url_prefix=None)
    app.register_blueprint(post.instance,url_prefix=None)
    app.register_blueprint(tag.instance,url_prefix=None)
    app.register_blueprint(feed.instance,url_prefix=None)
    app.register_blueprint(comment.instance,url_prefix=None)
    app.register_blueprint(activity.instance,url_prefix=None)

