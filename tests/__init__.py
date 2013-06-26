# -*- coding: utf-8 -*-

import unittest
import logging
import time
import hmac

from flask.ext.testing import TestCase as Base

from motiky import create_app
from motiky import configs
from motiky.configs import db,redis

class TestCase(Base):

    def create_app(self):
        app = create_app(configs.TestConfig)
        app.config['TESTING'] = True
        return app

    def generate_header(self,ukey):
        _now = int(time.time())
        token = '%s|%d|%s' % (ukey,_now,hmac.new(configs.TestConfig().APPLICATION_SECRET,
                        ukey+str(_now)).hexdigest())
        return {'X-MOTIKY-TOKEN':token}

    def setUp(self):
        db.create_all()
        redis.flushdb()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        print dir(redis)
