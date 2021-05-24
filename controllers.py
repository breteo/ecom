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
from .models import get_user_email, get_user, get_user_name
import uuid
import random

url_signer = URLSigner(session)

@action('home')
@action.uses(db, auth.user, 'home.html')
def home():
    rows = db(db.ebook).select(limitby=(0, 4)).as_list()

    for row in rows:
        prices = db(db.prices.ebook_id == row['id']).select().as_list()
        result = sys.maxsize
        for p in prices:
            if p['price'] < result:
                result = p['price']
        # and we can simply assign the nice string to a field of the row!
        # No matter that the field did not originally exist in the database.
        row["price"] = result

    popular = db(db.ebook).select(orderby=~db.ebook.purchased_count, limitby=(0, 4)).as_list()

    for pop in popular:
        prices = db(db.prices.ebook_id == pop['id']).select().as_list()
        result = sys.maxsize
        for p in prices:
            if p['price'] < result:
                result = p['price']
        # and we can simply assign the nice string to a field of the row!
        # No matter that the field did not originally exist in the database.
        pop["price"] = result

    return dict(rows=rows, popular=popular, url_signer=url_signer, search_url=URL('search', signer=url_signer),
                my_callback_url=URL('my_callback', signer=url_signer),
                add_post_url = URL('add_post', signer=url_signer),
                delete_post_url = URL('delete_post', signer=url_signer),
                get_rating_url = URL('get_rating', signer=url_signer),
                set_rating_url = URL('set_rating', signer=url_signer), theuser=get_user())

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

    return dict(rows=rows, url_signer=url_signer, search_url = URL('search', signer=url_signer),
                my_callback_url=URL('my_callback', signer=url_signer), add_post_url=URL('add_post', signer=url_signer),
                delete_post_url=URL('delete_post', signer=url_signer),
                get_rating_url=URL('get_rating', signer=url_signer),
                set_rating_url=URL('set_rating', signer=url_signer))


@action('my_callback')
@action.uses(url_signer.verify(), db)
def my_callback():
    rows = db(db.post).select().as_list()
    return dict(rows=rows, user=get_user_email(), the_reviewer=get_user())


@action('add_post', method="POST")
@action.uses(url_signer.verify(), db)
def add_post():
    #print(request.json.get('author'))
    id = db.post.insert(
        content=request.json.get('content'),
        reviewer=request.json.get('reviewer')
    )
    print(request.json.get('content'))
    return dict(id=id, author=get_user_name())


@action('delete_post')
@action.uses(url_signer.verify(), db)
def delete_post():
    id = request.params.get('id')
    assert id is not None
    db(db.post.id == id).delete()
    return "ok"


@action('get_rating')
@action.uses(url_signer.verify(), db, auth.user)
def get_rating():
    post_id = request.params.get('post_id')
    row = db((db.star_rev.post == post_id) &
             (db.star_rev.by == get_user())).select().first()
    rating = row.rating if row is not None else 0
    return dict(rating=rating)


@action('set_rating', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_rating():
    post_id = request.json.get('post_id')
    rating = request.json.get('rating')
    assert post_id is not None and rating is not None
    db.star_rev.update_or_insert(
        ((db.star_rev.post == post_id) & (db.star_rev.by == get_user())),
        post=post_id,
        by=get_user(),
        rating=rating
    )
    return "ok"

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
    isFound = False
    p = db.ebook[ebook_id]
    rows = db(db.wish_list.user_id == get_user()).select(db.wish_list.ebook_id).as_list()
    for row in rows:
        if(int(ebook_id) == int(row['ebook_id'])):
            isFound = True
            break
    if(isFound is False):
        db.wish_list.insert(ebook_id=ebook_id, user_id=get_user(), title=p.title, img=p.img, author=p.author, url=p.url)
    redirect(URL('index'))


@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    results = []
    rows = db(db.ebook).select(db.ebook.title).as_list()
    for row in rows:
        if(row['title'].lower().find(q.lower()) != -1):
            results.append(q + ": " + row['title'])
    return dict(results=results)


@action('gotowishlist')
@action.uses(db, session, auth.user, 'wishlist.html')
def gotowishlist():
    rows = db(db.wish_list.user_id == get_user()).select().as_list()

    for row in rows:
        prices = db(db.prices.ebook_id == row['ebook_id']).select().as_list()
        # print(prices)
        result = sys.maxsize
        for p in prices:
            if p['price'] < result:
                result = p['price']
        # and we can simply assign the nice string to a field of the row!
        # No matter that the field did not originally exist in the database.
        row["price"] = result

    return dict(rows=rows, url_signer=url_signer, search_url=URL('search', signer=url_signer))

@action('info/<ebook_id:int>')
@action.uses(db, auth.user, 'info.html')
def info(ebook_id=None):
    assert ebook_id is not None
    book = db.ebook[ebook_id]
    return dict(book=book, url_signer=url_signer)
