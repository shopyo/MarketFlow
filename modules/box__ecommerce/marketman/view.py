
from shopyoapi.module import ModuleHelp
# from flask import render_template
from flask import url_for
from flask import redirect
from flask import flash
from flask import request
from flask import current_app

# from shopyoapi.html import notify_success
# from shopyoapi.forms import flash_errors

from flask_login import login_required
from flask_login import current_user

from modules.box__ecommerce.store.models import Store
from modules.box__ecommerce.product.models import Product
from modules.box__ecommerce.product.models import ModerationMessage
from modules.box__ecommerce.shop.models import OrderItem
from shopyoapi.init import db
from shopyoapi.html import notify_warning

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]

# @module_blueprint.route("/")
# def index():
#     return mhelp.info['display_string']

# @wraps(func)
# def decorated_view(*args, **kwargs):
#     if current_app.login_manager._login_disabled:
#         return func(*args, **kwargs)
#     elif not current_user.is_authenticated():
#         return current_app.login_manager.unauthorized()
#     return func(*args, **kwargs)

@module_blueprint.after_request
def marketman_after_request(response):

    if current_app.login_manager._login_disabled:
        pass
    elif hasattr(current_user, 'is_authenticated'):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
    elif hasattr(current_user, 'is_authenticated'):
        if current_user.is_authenticated:
            if not current_user.is_admin:
                return redirect(url_for('auth.login'))
    
    return response

def num_status(status):
    return len(OrderItem.query.filter(OrderItem.status==status).all())

@module_blueprint.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    context = mhelp.context()
    stores = len(Store.query.all())
    products = len(Product.query.all())
    orders_pending = num_status('pending')
    orders_processing = num_status('processing')
    orders_shipped = num_status('shipped')
    orders_cancelled = num_status('cancelled')
    orders_refunded = num_status('refunded')
    context.update({
        'charts':{
            'orders':{
                'pending': orders_pending,
                'processing': orders_processing,
                'shipped': orders_shipped,
                'cancelled': orders_cancelled,
                'refunded': orders_refunded
            }
        },
        'num_stores': db.session.query(Store).count(), 
        'num_products': db.session.query(Product).count()
        })
    return mhelp.render('dashboard.html', **context)


@module_blueprint.route("store/unapproved/list", methods=["GET"])
@login_required
def list_unapproved_stores():

    context = mhelp.context()

    unapproved_stores = Store.query.filter(Store.is_verified == False).all()
    context.update({
        'unapproved_stores': unapproved_stores
        })
    return mhelp.render('unapproved_stores.html', **context)


@module_blueprint.route("store/<store_id>/view", methods=["GET"])
@login_required
def view_unapproved_store(store_id):

    context = mhelp.context()
    store = Store.query.get(store_id)
    context.update({
        'store': store
        })
    return mhelp.render('view_application.html', **context)


@module_blueprint.route("store/<store_id>/approve", methods=["GET"])
@login_required
def approve_store(store_id):
    store = Store.query.get(store_id)
    store.is_verified = True
    store.save()
    return mhelp.redirect_url(mhelp.method('list_unapproved_stores')) 

@module_blueprint.route("/unapproved/product/list/page/<int:page>")
@module_blueprint.route("/unapproved/product/list", methods=["GET"])
@login_required
def list_unapproved_product(page=1):

    context = mhelp.context()

    unapproved_products = Product.query.filter(Product.status == 'pending').all()
    
    PAGINATION = 5
    end = page * PAGINATION
    start = end - PAGINATION
    total_pages = (len(unapproved_products) // PAGINATION) + 1
    unapproved_products = unapproved_products[::-1][start:end]

    context.update(
        {
            "unapproved_products": unapproved_products,
            "total_pages": total_pages,
            "page": page
        }
    )
    return mhelp.render('unapproved_products.html', **context)


@module_blueprint.route("/product/<product_id>/pending/view/rtp/<rtpage>", methods=["GET"])
@login_required
def view_unapproved_product(product_id, rtpage):

    context = mhelp.context()
    product = Product.query.get(product_id)
    context.update({
        'product': product,
        'rtpage': rtpage
        })
    return mhelp.render('unapproved_product_view.html', **context)


@module_blueprint.route("/product/<product_id>/approve/rtpage/<rtpage>", methods=["GET"])
@login_required
def approve_product(product_id, rtpage):
    p = Product.query.get(product_id)
    p.set_status_approved()
    p.update()
    return mhelp.redirect_url('marketman.list_unapproved_product', page=rtpage)


@module_blueprint.route("/product/<product_id>/reject/rtpage/<rtpage>", methods=["GET", "POST"])
@login_required
def reject_product(product_id, rtpage):
    if request.method == 'POST':
        text = request.form['text']
        if not text.strip():
            flash(notify_warning('Message cannot be empty'))
            return mhelp.redirect_url('marketman.view_unapproved_product', product_id=product_id, rtpage=rtpage)
        p = Product.query.get(product_id)
        p.set_status_not_submitted()
        p.moderation_messages.append(ModerationMessage(text=text))
        p.update()
        return mhelp.redirect_url('marketman.list_unapproved_product', page=rtpage)