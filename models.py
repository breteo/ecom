"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()

def get_user():
    return auth.current_user.get('id') if auth.current_user else None

def get_user_name():
    return (auth.current_user.get('first_name') + " " + auth.current_user.get('last_name')) if auth.current_user else None


db.define_table(
    'ebook',
    Field('title', requires=IS_NOT_EMPTY()),
    Field('url', requires=IS_NOT_EMPTY()),
    Field('img', default='no-image.jpg'),
    Field('author', requires=IS_NOT_EMPTY()),
    Field('description'),
    Field('purchased_count', 'integer', requires=IS_NOT_EMPTY())
)

db.define_table(
    'prices',
    Field('ebook_id'),
    Field('price', 'integer'),
    Field('source', requires=IS_NOT_EMPTY())
)

db.define_table(
    'shopping_cart',
    Field('user_id', requires=IS_NOT_EMPTY()),
    Field('ebook_id'),
    Field('title', requires=IS_NOT_EMPTY()),
    Field('url', requires=IS_NOT_EMPTY()),
    Field('img', default=IS_NOT_EMPTY),
    Field('author', requires=IS_NOT_EMPTY()),
    Field('description'),
)

db.define_table(
    'wish_list',
    Field('user_id', requires=IS_NOT_EMPTY(), default=get_user),
    Field('ebook_id'),
    Field('title', requires=IS_NOT_EMPTY()),
    Field('url', requires=IS_NOT_EMPTY()),
    Field('img', default=IS_NOT_EMPTY),
    Field('author', requires=IS_NOT_EMPTY()),
)

db.define_table(
    'post',
    Field('content', 'text'),
    Field('author', default=get_user_name),
    Field('owner', default=get_user_email),
    Field('reviewer', default=get_user),

)

db.define_table(
    'star_rev',
    Field('by', default=get_user_name),
    Field('post', 'reference post'),
    Field('rating', 'integer', default=0) #0-5
)

db.define_table(
    'prod_post',
    Field('content', 'text'),
    Field('author', default=get_user_name),
    Field('owner', default=get_user_email),
    Field('reviewer', default=get_user),
    Field('ebook_id'),
)

db.define_table(
    'prod_star_rev',
    Field('by', default=get_user_name),
    Field('prod_post', 'reference prod_post'),
    Field('rating', 'integer', default=0) #0-5
)


db.commit()
