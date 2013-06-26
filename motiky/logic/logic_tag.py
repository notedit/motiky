# -*- coding: utf-8 -*-
# author: notedit
# date: 2013-04-10

import types
import traceback

from motiky.coreutil import BackendError,register,assert_error

from motiky.logic.models import User,Post,Tag,Tagging

from motiky.configs import db

# 99999999  编辑推荐
# 99999998  热门
# 这里应该排除推荐推荐和热门
@register('get_all_tags')
def get_all_tags():
    tags = Tag.query.filter(Tag.show == True).\
            filter(db.not_(Tag.id.in_([99999999,99999998]))).\
            order_by(Tag.order_seq.desc()).all()
    return [tag.json for tag in tags]

@register('get_recommend_tags')
def get_recommend_tags():
    tags = Tag.query.filter(Tag.show == True).\
            filter(Tag.recommended == True).\
            order_by(Tag.order_seq.desc()).all()
    return [tag.json for tag in tags]

@register('get_tag')
def get_tag(tag_id):
    assert_error(type(tag_id) == types.IntType,'ParamError')
    tag = Tag.query.get(tag_id)
    return tag.json

@register('get_tag_post_count')
def get_tag_post_count(tag_id):
    assert_error(type(tag_id) == types.IntType,'ParamError')
    count = Tagging.query.filter(Tagging.tag_id == tag_id).count()
    return count

@register('get_tag_post')
def get_tag_post(tag_id,limit=10,offset=0):
    assert_error(offset>=0,'ParamError')
    posts = Post.query.join(Tagging,Post.id == Tagging.taggable_id).\
            filter(Tagging.tag_id == tag_id).\
            filter(Post.show == True).\
            order_by(Tagging.date_create.desc()).\
            limit(limit).offset(offset).all()
    return [p.json for p in posts];

def _get_tag_id(tagstr):
    tag = Tag.query.filter(Tag.name == tagstr).first()
    if tag:
        return tag.id
    _tag = Tag(name=tagstr)
    try:
        db.session.add(_tag)
        db.session.commit()
    except:
        pass
    else:
        return _tag.id

    return None

@register('add_post_tag')
def add_post_tag(post_id,tags):
    for tag in tags:
        t = _get_tag_id(tag)
        if t is None:
            continue
        try:
            tagging = Tagging(taggable_id=post_id,tag_id=t)
            db.session.add(tagging)
            db.session.commit()
        except:
            db.session.rollback()



