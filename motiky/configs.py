# -*- coding: utf-8 -*-

import socket
import datetime

from redis import Redis
from rq import Connection,Queue
from flask.ext.redis import Redis as fRedis
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from flask.ext.mail import Mail

db = SQLAlchemy()
cache = Cache()
mail = Mail()
redis = fRedis()
rq = Queue('motiky',connection=Redis())

class DefaultConfig(object):

    DEBUG = False
    SECRET_KEY = 'lifeistooshorttowait'
    APPLICATION_SECRET = 'lifeistooshorttowait'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/motiky'
    SQLALCHEMY_ECHO = False

class TestConfig(object):
    CONFIG_TYPE = 'test'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/test'
    SQLALCHEMY_ECHO = False
    APPLICATION_SECRET = 'lifeistooshorttowait'
    CSRF_ENABLED = False
    VIDEO_URL_PREFIX = 'http://localhost'

class DevConfig(object):
    CONFIG_TYPE = 'dev'
    SQLALCHEMY_DATABASE_URI = \
            'postgresql+psycopg2://user:password@localhost/motiky'

class ProductionConfig(object):
    CONFIG_TYPE = 'production'
    SQLALCHEMY_ECHO = False
    VIDEO_URL_PREFIX = 'http://motiky01.b0.upaiyun.com'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/motiky'
    DEBUG = True

