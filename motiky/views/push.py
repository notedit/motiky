# -*- coding: utf-8 -*-

# author: notedit <notedit@gmail.com>

import sys 
import time
import logging

import flask
from flask import g
from flask import request
from flask import redirect
from flask import Response
from flask import current_app
from flask import session
from flask import jsonify
from flask import flash
from flask.views import MethodView
from flask.views import View

from missing import authutil
from missing.site import instance
from missing.logic import backend
from missing.coreutil import BackendError
from missing.configs import redis,rq

instance = Blueprint('push',__name__)


@instance.route('/push',methods=('POST',))
def push():
    """
    user_id:int
    data:{
        'alert':str,
        'sound':str,
        'custom':dict
    }
    https://github.com/simonwhitaker/PyAPNs
    """
    if not request.json:
        return jsonify(error='content-type should be json')
    if not set(['user_id','data']).issubset(set(request.json.keys())):
        return jsonify(error='params error')

    user_id = request.json['user_id']
    data = request.json['data']

    rq.enqueue('onepiece.worker.apns_push',user_id=user_id,data=data)
    
    return jsonify(ok='push is in the queue')
