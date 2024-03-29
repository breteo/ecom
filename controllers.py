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
from .settings import APP_FOLDER, APP_NAME
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user, get_user_name
import json
import os
import stripe

url_signer = URLSigner(session)

with open(os.path.join(APP_FOLDER, 'private', 'stripe_keys.json'), 'r') as f:
    STRIPE_KEY_INFO = json.load(f)
stripe.api_key = STRIPE_KEY_INFO['test_private_key']

def full_url(u):
    p = request.urlparts
    return p.scheme + "://" + p.netloc + u

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

    popular = db(db.ebook).select(
        orderby=~db.ebook.purchased_count, limitby=(0, 4)).as_list()

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
                add_post_url=URL('add_post', signer=url_signer),
                delete_post_url=URL('delete_post', signer=url_signer),
                get_rating_url=URL('get_rating', signer=url_signer),
                set_rating_url=URL('set_rating', signer=url_signer), theuser=get_user())


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

    return dict(rows=rows, url_signer=url_signer, search_url=URL('search', signer=url_signer),
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
    # print(request.json.get('author'))
    id = db.post.insert(
        content=request.json.get('content'),
        reviewer=request.json.get('reviewer')
    )
    # print(request.json.get('content'))
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
    row = db((db.star_rev.post == post_id)).select().first()
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
    isFound = False
    p = db.ebook[ebook_id]
    rows = db(db.shopping_cart.user_id == get_user()).select(
        db.shopping_cart.ebook_id).as_list()
    for row in rows:
        if(int(ebook_id) == int(row['ebook_id'])):
            isFound = True
            break
    if(isFound is False):
        db.shopping_cart.insert(ebook_id=ebook_id, user_id=get_user(
        ), title=p.title, img=p.img, author=p.author, url=p.url, description=p.description)
    redirect(URL('index'))


@action('add_to_wishlist/<ebook_id:int>')
@action.uses(db, auth.user)
def add_to_wishlist(ebook_id=None):
    assert ebook_id is not None
    isFound = False
    p = db.ebook[ebook_id]
    rows = db(db.wish_list.user_id == get_user()).select(
        db.wish_list.ebook_id).as_list()
    for row in rows:
        if(int(ebook_id) == int(row['ebook_id'])):
            isFound = True
            break
    if(isFound is False):
        db.wish_list.insert(ebook_id=ebook_id, user_id=get_user(
        ), title=p.title, img=p.img, author=p.author, url=p.url)
    redirect(URL('index'))


@action('search')
@action.uses()
def search():
    q = request.params.get("q")
    results = []
    rows = db(db.ebook).select(db.ebook.title, db.ebook.id).as_list()
    # print(rows)
    for row in rows:
        # print(row['title'])
        if(row['title'].lower().find(q.lower()) != -1):
            results.append(tuple((row['title'], row['id'])))
    # print(results)
    return dict(results=results)


@action('gotowishlist')
@action.uses(db, session, auth.user, 'wishlist.html')
def gotowishlist():
    rows = db(db.wish_list.user_id == get_user()).select().as_list()
    # print(rows)

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


@action('gotocart')
@action.uses(db, session, auth.user, 'cart.html')
def gotocart():
    rows = db(db.shopping_cart.user_id == get_user()).select().as_list()
    total = 0

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
        total = total + result

    return dict(rows=rows, url_signer=url_signer, total=total, search_url=URL('search', signer=url_signer),
                stripe_key=STRIPE_KEY_INFO['test_public_key'],
                pay_url=URL('pay', signer=url_signer),
                app_name=APP_NAME)


@action('info/<ebook_id:int>')
@action.uses(db, auth.user, 'info.html')
def info(ebook_id=None):
    assert ebook_id is not None
    book = db.ebook[ebook_id]
    return dict(book=book, url_signer=url_signer, ebook_id=ebook_id, load_bookrev_url=URL('load_bookrev', signer=url_signer),
                add_book_url=URL('add_book', signer=url_signer),
                delete_book_url=URL('delete_book', signer=url_signer),
                get_rev_rating_url=URL('get_rev_rating', signer=url_signer),
                set_rev_rating_url=URL('set_rev_rating', signer=url_signer),)


@action('load_bookrev')
@action.uses(url_signer.verify(), db)
def load_bookrev():
    rows = db(db.prod_post).select().as_list()
    return dict(rows=rows, user=get_user_email(), the_reviewer=get_user())


@action('add_book', method="POST")
@action.uses(url_signer.verify(), db)
def add_book():
    # print(request.json.get('author'))
    id = db.prod_post.insert(
        content=request.json.get('content'),
        reviewer=request.json.get('reviewer'),
        ebook_id=request.json.get('ebook_id')
    )
    # print(request.json.get('content'))
    return dict(id=id, author=get_user_name())


@action('delete_book')
@action.uses(url_signer.verify(), db)
def delete_book():
    id = request.params.get('id')
    assert id is not None
    db(db.prod_post.id == id).delete()
    return "ok"


@action('get_rev_rating')
@action.uses(url_signer.verify(), db, auth.user)
def get_rev_rating():
    prod_post_id = request.params.get('prod_post_id')
    row = db((db.prod_star_rev.prod_post == prod_post_id)).select().first()
    rating = row.rating if row is not None else 0
    return dict(rating=rating)


@action('set_rev_rating', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_rev_rating():
    prod_post_id = request.json.get('prod_post_id')
    rating = request.json.get('rating')
    assert prod_post_id is not None and rating is not None
    db.prod_star_rev.update_or_insert(
        ((db.prod_star_rev.prod_post == prod_post_id)
         & (db.prod_star_rev.by == get_user())),
        prod_post=prod_post_id,
        by=get_user(),
        rating=rating
    )
    return "ok"


@action('delete_wishlist/<wish_list_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_wishlist(wish_list_id=None):
    assert wish_list_id is not None
    db((db.wish_list.user_id == get_user()) & (
        db.wish_list.id == wish_list_id)).delete()
    redirect(URL('gotowishlist'))


@action('delete_cart/<shopping_cart_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_cart(shopping_cart_id=None):
    assert shopping_cart_id is not None
    db((db.shopping_cart.user_id == get_user()) & (
        db.shopping_cart.id == shopping_cart_id)).delete()
    redirect(URL('gotocart'))

@action('clear_cart/<shopping_cart_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def clear_cart(shopping_cart_id=None):
    assert shopping_cart_id is not None
    db((db.shopping_cart.user_id == get_user())).delete()
    redirect(URL('gotocart'))

@action('pay', method="POST")
@action.uses(db, url_signer.verify())
def pay():
    # See https://stripe.com/docs/payments/checkout/migration#api-products
    # Insert non-paid order (the customer has not checked out yet).
    rows = db(db.shopping_cart.user_id == get_user()).select().as_list()
    line_items = []
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
        line_item = {
            'quantity': int(1),
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(row["price"] * 100),  # Stripe wants int.
                'product_data': {
                    'name': row['title'],
                }
            }
        }
        line_items.append(line_item)
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=full_url(URL('successful_payment', signer=url_signer)),
        cancel_url=full_url(URL('cancelled_payment', signer=url_signer))
    )
    return dict(session_id=stripe_session.id)

@action('successful_payment')
@action.uses(db, session, auth.user,url_signer.verify())
def successful_payment():
    db((db.shopping_cart.user_id == get_user())).delete()
    redirect(URL('home'))

@action('cancelled_payment')
@action.uses(url_signer.verify())
def cancelled_payment():
    redirect(URL('home'))
