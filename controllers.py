"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
import sys

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
import uuid
import random

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    rows = db(db.ebook).select().as_list()

    for row in rows:
        prices = db(db.prices.ebook_id == row['id']).select().as_list()
        result = sys.maxsize
        for p in prices:
            if p['price'] < result:
                result = p['price']
        # and we can simply assign the nice string to a field of the row!
        # No matter that the field did not originally exist in the database.
        row["price"] = result

    return dict(rows=rows, url_signer=url_signer, search_url = URL('search', signer=url_signer))

@action('add_to_cart/<ebook_id:int>')
@action.uses(db, auth.user)
def add_to_cart(ebook_id=None):
    assert ebook_id is not None
    uid = db.auth_user(email = get_user_email()).select('id')
    db.shopping_cart.insert(
        user_id=uid,
        ebook_id=ebook_id
    )
    redirect(URL('index'))

@action('add_to_wishlist/<ebook_id:int>')
@action.uses(db, auth.user)
def add_to_wishlist(ebook_id=None):
    assert ebook_id is not None
    uid = db.auth_user(email = get_user_email()).select('id')
    db.wish_list.insert(
        user_id=uid,
        ebook_id=ebook_id
    )
    redirect(URL('index'))

@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    results = [q + ":" + str(uuid.uuid1()) for _ in range(random.randint(2, 6))]
    return dict(results=results)