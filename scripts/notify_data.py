#/usr/bin/evn python
# -*- coding: utf-8 -*-

import os
import sys
import json
import traceback

sys.path.insert(0,'../')

from komandr import *

from motiky.logic.models import User,Post,Comment,Activity

from motiky import create_app
from motiky import configs
from motiky.configs import db

app = create_app(configs.ProductionConfig)

@command('generate_notify_data')
def generate_notify_data():
    pass


main()
