# -*- coding: utf-8 -*-


# add your models here
import os
import uuid
import contextlib
from datetime import datetime

from flask import current_app
from werkzeug import cached_property
from sqlalchemy.dialects.postgresql import ARRAY,UUID

from motiky.configs import db,DefaultConfig

DATE_FMT = '%Y-%m-%d %H:%M:%S'
DATE_DEFAULT = '2013-05-30 12:00:00'

def format_date(date):
    return date.strftime(DATE_FMT) if date else DATE_DEFAULT

class User(db.Model):

    __tablename__ = 'user_info'    
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50),unique=True)
    photo_url = db.Column(db.String(100))
    signature = db.Column(db.String(255))
    status = db.Column(db.String(20))
    uid = db.Column(db.String(100),index=True,unique=True)
    push_on = db.Column(db.Boolean,default=True)
    access_token = db.Column(db.String(128))
    date_create = db.Column(db.DateTime,default=datetime.now)
    date_update = db.Column(db.DateTime,default=datetime.now)

    @cached_property
    def json(self):
        return dict(id=self.id,
                    username=self.username,
                    email=self.email,
                    photo_url=self.photo_url,
                    signature=self.signature,
                    status=self.status,
                    uid=str(self.uid),
                    push_on=self.push_on,
                    access_token=self.access_token,
                    date_create=format_date(self.date_create),
                    date_update=format_date(self.date_update))


class Post(db.Model):

    __tablename__ = 'post'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(300))
    pic_small = db.Column(db.String(255))
    pic_big = db.Column(db.String(255))
    video_url = db.Column(db.String(255))
    author_id = db.Column(db.Integer,db.ForeignKey(User.id),index=True)
    show = db.Column(db.Boolean,default=True,index=True)
    recommended = db.Column(db.Boolean,default=False,index=True)
    play_count = db.Column(db.Integer,default=0)
    date_create = db.Column(db.DateTime,default=datetime.now)
    date_update = db.Column(db.DateTime,default=datetime.now)
    date_publish = db.Column(db.DateTime,default=datetime.now)
    user = db.relation(User, innerjoin=True, lazy="joined")

    @cached_property
    def json(self):
        video_prefix = current_app.config.get('VIDEO_URL_PREFIX') if current_app \
                else DefaultConfig.VIDEO_URL_PREFIX
        return dict(id=self.id,
                    title=self.title,
                    pic_big=self.pic_big,
                    pic_small=os.path.join(video_prefix,self.pic_small or ''),
                    video_url=os.path.join(video_prefix,self.video_url or ''),
                    author_id=self.author_id,
                    show=self.show,
                    recommended=self.recommended,
                    play_count=self.play_count,
                    date_create=format_date(self.date_create),
                    date_update=format_date(self.date_update),
                    date_publish=format_date(self.date_publish))


class Report(db.Model):

    __tablename__ = 'report'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(User.id),index=True)
    post_id = db.Column(db.Integer,db.ForeignKey(Post.id),index=True)
    user = db.relation(User,innerjoin=True,lazy='joined')
    post = db.relation(Post,innerjoin=True,lazy='joined')
    date_create = db.Column(db.DateTime,default=datetime.now)


class Install(db.Model):

    __tablename__ = 'install'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(User.id),index=True,unique=True)
    version = db.Column(db.String(20))
    badge = db.Column(db.Integer,default=0)
    device_token = db.Column(db.String(100),index=True)
    device_type = db.Column(db.String(20))
    date_create = db.Column(db.DateTime,default=datetime.now)

    @property
    def json(self):
        return dict(id=self.id,
                    user_id=self.user_id,
                    version=self.version,
                    badge=self.badge,
                    device_token=self.device_token,
                    device_type=self.device_type,
                    date_create=format_date(self.date_create))


class UserFollowAsso(db.Model):

    __tablename__ = 'user_follow_asso'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(User.id),index=True)
    user_id_to = db.Column(db.Integer,db.ForeignKey(User.id),index=True)
    date_create = db.Column(db.DateTime,default=datetime.now)

    __table_args__ = (
            db.UniqueConstraint('user_id','user_id_to'),
            )


class UserLikeAsso(db.Model):
    
    __tablename__ = 'user_like_asso'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey(User.id),index=True)
    post_id = db.Column(db.Integer,db.ForeignKey(Post.id),index=True)
    date_create = db.Column(db.DateTime,default=datetime.now)

    __table_args__ = (
            db.UniqueConstraint('user_id','post_id'),
            )

class UserPlayAsso(db.Model):

    __tablename__ = 'user_play_asso'
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)
    date_create = db.Column(db.DateTime,default=datetime.now)


class Comment(db.Model):

    __tablename__ = 'comment'
    id = db.Column(db.Integer,primary_key=True)
    post_id = db.Column(db.Integer,index=True)
    author_id = db.Column(db.Integer,db.ForeignKey(User.id))
    content = db.Column(db.String(1000))
    show = db.Column(db.Boolean,default=True)
    date_create = db.Column(db.DateTime,default=datetime.now)

    @cached_property
    def json(self):
        return dict(id=self.id,
                    post_id=self.post_id,
                    author_id=self.author_id,
                    content=self.content,
                    show=self.show,
                    date_create=format_date(self.date_create))


class Activity(db.Model):

    __tablename__ = 'activity'
    id = db.Column(db.Integer,primary_key=True)
    post_id = db.Column(db.Integer)
    comment_id = db.Column(db.Integer)
    from_id = db.Column(db.Integer)
    to_id = db.Column(db.Integer)
    atype = db.Column(db.String(20))
    # atype follow  like comment  post_reco text 
    date_create = db.Column(db.DateTime,default=datetime.now)

    @cached_property
    def json(self):
        return dict(id=self.id,
                    post_id=self.post_id,
                    comment_id=self.comment_id,
                    from_id=self.from_id,
                    to_id=self.to_id,
                    atype=self.atype,
                    date_create=format_date(self.date_create))


class Action(db.Model):

    __tablename__ = 'action'
    id = db.Column(db.Integer,primary_key=True)
    post_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer,index=True)
    atype = db.Column(db.String(20),index=True)
    payload = db.Column(db.String(255))
    date_create = db.Column(db.DateTime,default=datetime.now)

    @cached_property
    def json(self):
        return dict(id=self.id,
                    post_id=self.post_id,
                    user_id=self.user_id,
                    atype=self.atype,
                    payload=self.payload,
                    date_create=format_date(self.date_create))


class Tag(db.Model):

    __tablename__ = 'tag'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255),index=True)
    show = db.Column(db.Boolean,default=True)
    pic_url = db.Column(db.String(255))
    order_seq = db.Column(db.Integer,default=0)
    recommended = db.Column(db.Boolean,default=False)
    date_create = db.Column(db.DateTime,default=datetime.now)
    
    @cached_property
    def json(self):
        return dict(id=self.id,
                    name=self.name,
                    show=self.show,
                    pic_url=self.pic_url,
                    order_seq=self.order_seq,
                    recommended=self.recommended,
                    date_create=format_date(self.date_create))


class Tagging(db.Model):

    __tablename__ = 'tagging'
    id = db.Column(db.Integer,primary_key=True)
    taggable_type = db.Column(db.String(20))
    taggable_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    date_create = db.Column(db.DateTime,default=datetime.now)

    @cached_property
    def json(self):
        return dict(id=self.id,
                    taggable_type=self.taggable_type,
                    taggalbe_id=self.taggable_id,
                    tag_id=self.tag_id,
                    user_id=self.user_id,
                    date_create=format_date(self.date_create))


class Storage(db.Model):
    __tablename__ = 'storage'
    id = db.Column(UUID(),default=lambda:str(uuid.uuid4()),primary_key=True)
    file_md5 = db.Column(db.String(80))
    file_size = db.Column(db.Integer)
    date_create = db.Column(db.DateTime,default=datetime.now)


class CmsUser(db.Model):
    __tablename__ = 'cms_user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(80))
    date_create = db.Column(db.DateTime,default=datetime.now)



