# -*- coding: utf-8 -*-

# the schema for motiky's api

import colander
from datetime import datetime
from colander import SchemaNode,MappingSchema,SequenceSchema
from colander import Int,Date,String,Bool,DateTime
from colander import Range,Length

class IdListSchema(SequenceSchema):
    id = SchemaNode(Int(),validator=Range(min=1))

class StrListSchema(SequenceSchema):
    _str = SchemaNode(String())

class LimitOffsetSchema(MappingSchema):
    offset = SchemaNode(Int())
    limit = SchemaNode(Int())

class NewUserSchema(MappingSchema):
    uid = SchemaNode(String())
    access_token = SchemaNode(String(),missing=u'')

class UpdateUserSchema(MappingSchema):
    username = SchemaNode(String(encoding='utf-8'),missing=None)
    photo_url = SchemaNode(String(encoding='utf-8'),missing=None)
    signature = SchemaNode(String(encoding='utf-8'),missing=None)
    access_token = SchemaNode(String(encoding='utf-8'),missing=u'')
    status = SchemaNode(String(encoding='utf-8'),missing=None)
    date_update = SchemaNode(DateTime(),missing=None)

class UserFollowSchema(MappingSchema):
    user_ids = IdListSchema()

class InstallSchema(MappingSchema):
    device_type = SchemaNode(String())
    device_token = SchemaNode(String())
    version = SchemaNode(String())
    user_id = SchemaNode(Int())


class PushSchema(MappingSchema):
    user_id = SchemaNode(Int())
    install_id = SchemaNode(String())
    action = SchemaNode(String())
    
class NewPostSchema(MappingSchema):
    title = SchemaNode(String(),missing=None)
    author_id = SchemaNode(Int())
    #tag_id = SchemaNode(Int(),missing=None)

class UpdatePostSchema(MappingSchema):
    title = SchemaNode(String(encoding='utf-8'),missing=None)
    author_id = SchemaNode(Int(),missing=None)
    pic_small = SchemaNode(String(encoding='utf-8'),missing=None)
    date_update = SchemaNode(DateTime(),missing=datetime.now())

class NewCommentSchema(MappingSchema):
    post_id = SchemaNode(Int())
    author_id = SchemaNode(Int())
    content = SchemaNode(String())

class PostLikeSchema(MappingSchema):
    user_id = SchemaNode(Int())
    post_id = SchemaNode(Int())

class PostUnlikeSchema(MappingSchema):
    user_id = SchemaNode(Int())
    post_id = SchemaNode(Int())


