import os
import sys
from flask import current_app
from flask.ext.script import Manager,prompt,prompt_pass,\
        prompt_bool,prompt_choices
from flask.ext.script import Server
from werkzeug import generate_password_hash,check_password_hash

from motiky import configs
from motiky.configs import db
from motiky import create_app

from motiky.logic.models import CmsUser

app = create_app(configs.ProductionConfig)
manager = Manager(app)

@manager.command
def create_all():
    if prompt_bool("Are you sure? You will init your database"):
        db.create_all()

@manager.command
def drop_all():
    if prompt_bool("Are you sure? You will lose all your data!"):
        db.drop_all()

@manager.option('-u','--username',dest='username',required=True)
@manager.option('-p','--password',dest='password',required=True)
@manager.option('-e','--email',dest='email',required=True)
def createuser(username=None,password=None,email=None):
    password = generate_password_hash(password)
    cmsuser = CmsUser(username=username,password=password,email=email)
    db.session.add(cmsuser)
    db.session.commit()
    print 'cms user was created'

manager.add_command('runserver',Server())

if __name__ == '__main__':
    manager.run()
