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


db.define_table(
    'ebook',
    Field('title', requires=IS_NOT_EMPTY()),
    Field('url', requires=IS_NOT_EMPTY()),
    Field('img', default=IS_NOT_EMPTY),
    Field('author', requires=IS_NOT_EMPTY()),
    Field('price', 'integer', requires=IS_NOT_EMPTY()),
    Field('purchased_count', 'integer', requires=IS_NOT_EMPTY())
)

db.define_table(
    'shopping_cart',
    Field('user_id', requires=IS_NOT_EMPTY()),
    Field('ebook_id')
)

db.define_table(
    'wish_list',
    Field('user_id', requires=IS_NOT_EMPTY()),
    Field('ebook_id')
)



db.commit()
