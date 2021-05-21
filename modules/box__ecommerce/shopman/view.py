 # from flask import render_template
# from flask import url_for
# from flask import redirect

import json
import os
import uuid

from sqlalchemy import desc

from flask import current_app
from flask import flash
from flask import request
from flask import url_for
from flask import session
from flask import redirect

import pandas as pd

from flask_login import login_required

import flask_uploads

from shopyoapi.enhance import get_setting
from shopyoapi.enhance import set_setting
from shopyoapi.forms import flash_errors
from shopyoapi.init import productphotos
from shopyoapi.file import unique_filename
from shopyoapi.init import db
from werkzeug.utils import secure_filename
from shopyoapi.init import storelogophotos
from shopyoapi.init import storebannerphotos
from shopyoapi.file import unique_sec_filename

# #
from shopyoapi.html import notify_success
from shopyoapi.html import notify_warning
from shopyoapi.file import delete_file
from shopyoapi.module import ModuleHelp

from modules.box__ecommerce.product.models import Product
from modules.box__ecommerce.shop.models import Order
from modules.box__ecommerce.shop.models import OrderItem
from modules.box__ecommerce.shopman.forms import CouponForm
from modules.box__ecommerce.shopman.forms import CurrencyForm
from modules.box__ecommerce.shopman.forms import DeliveryOptionForm
from modules.box__ecommerce.shopman.forms import PaymentOptionForm
from modules.box__ecommerce.store.models import Store
from modules.box__ecommerce.category.models import Category
from modules.box__ecommerce.category.models import SubCategory
from modules.resource.models import Resource

from .models import Coupon
from .models import DeliveryOption
from .models import PaymentOption

mhelp = ModuleHelp(__file__, __name__)

globals()[mhelp.blueprint_str] = mhelp.blueprint

module_blueprint = globals()[mhelp.blueprint_str]


def get_product(barcode):
    return Product.query.get(barcode)

def num_status(status, store_id):
    return len(OrderItem.query.filter(
        (OrderItem.status==status) &
        (OrderItem.store_id==store_id) ).all())



@module_blueprint.route('<store_id>'+mhelp.info["dashboard"])
@login_required
def dashboard(store_id):

    context = mhelp.context()
    orders_pending = num_status('pending', store_id)
    orders_processing = num_status('processing', store_id)
    orders_shipped = num_status('shipped', store_id)
    orders_cancelled = num_status('cancelled', store_id)
    orders_refunded = num_status('refunded', store_id)
    #sorted_items = OrderItem.query.order_by(desc(OrderItem.time)).all()
    context.update({'charts':{
            'orders':{
                'pending': orders_pending,
                'processing': orders_processing,
                'shipped': orders_shipped,
                'cancelled': orders_cancelled,
                'refunded': orders_refunded
            }
        }
        })
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id),
        'store_id': store_id})
    return mhelp.render("dashboard.html", **context)


@module_blueprint.route("currency/set", methods=["GET", "POST"])
@login_required
def set_currency():
    if request.method == "POST":
        form = CurrencyForm()
        set_setting("CURRENCY", form.currency.data)
        return mhelp.redirect_url("shopman.dashboard")


@module_blueprint.route("/delivery" + mhelp.info["dashboard"])
@login_required
def delivery():
    context = mhelp.context()
    form = DeliveryOptionForm()
    options = DeliveryOption.query.all()

    context.update({"form": form, "options": options})
    return mhelp.render("delivery.html", **context)


@module_blueprint.route("/delivery/option/add", methods=["GET", "POST"])
@login_required
def delivery_add_option():
    if request.method == "POST":
        form = DeliveryOptionForm()
        if form.validate_on_submit():
            toadd = DeliveryOption()
            toadd.option = form.option.data
            toadd.price = float(form.price.data)
            toadd.insert()
            flash(notify_success("Option Added!"))
            return mhelp.redirect_url("shopman.delivery")
        else:
            flash_errors(form)
            return mhelp.redirect_url("shopman.delivery")


@module_blueprint.route("/delivery/option/update", methods=["GET", "POST"])
@login_required
def delivery_option_update():
    if request.method == "POST":

        opt_id = request.form["id"]
        option_data = request.form["option"]
        price_data = request.form["price"]

        option = DeliveryOption.query.get(opt_id)
        option.option = option_data
        option.price = price_data
        option.update()

        flash(notify_success("Option updated!"))
        return mhelp.redirect_url("shopman.delivery")


@module_blueprint.route("/delivery/option/<option_id>/delete", methods=["GET"])
@login_required
def delivery_option_delete(option_id):
    option = DeliveryOption.query.get(option_id)
    option.delete()

    flash(notify_success("Option Deleted!"))
    return mhelp.redirect_url("shopman.delivery")


@module_blueprint.route("/payment/dashboard", methods=["GET", "POST"])
@login_required
def payment():
    context = mhelp.context()
    form = PaymentOptionForm()
    options = PaymentOption.query.all()

    context.update({"form": form, "options": options})
    return mhelp.render("payment.html", **context)


@module_blueprint.route("/payment/option/add", methods=["GET", "POST"])
@login_required
def payment_add_option():
    if request.method == "POST":
        form = PaymentOptionForm()
        if form.validate_on_submit():
            toadd = PaymentOption()
            toadd.name = form.name.data
            toadd.text = form.text.data
            toadd.insert()
            flash(notify_success("Option Added!"))
            return mhelp.redirect_url("shopman.payment")
        else:
            flash_errors(form)
            return mhelp.redirect_url("shopman.payment")


@module_blueprint.route("/payment/option/update", methods=["GET", "POST"])
@login_required
def payment_option_update():
    if request.method == "POST":

        opt_id = request.form["id"]
        option_data = request.form["name"]
        text_data = request.form["text"]

        option = PaymentOption.query.get(opt_id)
        option.name = option_data
        option.text = text_data
        option.update()

        flash(notify_success("Option updated!"))
        return mhelp.redirect_url("shopman.payment")


@module_blueprint.route("/payment/option/<option_id>/delete", methods=["GET"])
@login_required
def payment_option_delete(option_id):
    option = PaymentOption.query.get(option_id)
    option.delete()

    flash(notify_success("Option Deleted!"))
    return mhelp.redirect_url("shopman.payment")


@module_blueprint.route("/s/<store_id>/coupon/dashboard", methods=["GET", "POST"])
@login_required
def coupon(store_id):
    form = CouponForm()
    coupons = Coupon.query.filter(Coupon.store_id == store_id)
    context = mhelp.context()
    context.update({"form": form, "coupons": coupons, "store_id": store_id})
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id)})
    return mhelp.render("coupon.html", **context)


@module_blueprint.route("/s/<store_id>/coupon/add", methods=["GET", "POST"])
@login_required
def coupon_add(store_id):
    if request.method == "POST":
        form = CouponForm()
        if form.validate_on_submit():
            toadd = Coupon()
            toadd.string = form.string.data
            toadd.type = form.type.data
            toadd.value = form.value.data
            store = Store.query.get(store_id)
            toadd.coupon_store = store
            toadd.insert()
            flash(notify_success("Coupon Added!"))
            return mhelp.redirect_url("shopman.coupon", store_id=store_id)
        else:
            flash_errors(form)
            return mhelp.redirect_url("shopman.coupon", store_id=store_id)


@module_blueprint.route("/s/<store_id>/coupon/<coupon_id>/delete", methods=["GET"])
@login_required
def coupon_delete(store_id, coupon_id):
    coupon = Coupon.query.get(coupon_id)
    coupon.delete()

    flash(notify_success("Coupon Deleted!"))
    return mhelp.redirect_url("shopman.coupon", store_id=store_id)


@module_blueprint.route("/coupon/update", methods=["GET", "POST"])
@login_required
def coupon_update():
    if request.method == "POST":
        form = CouponForm()
        if form.validate_on_submit:
            coupon_id = request.form["id"]
            coupon = Coupon.query.get(coupon_id)
            coupon.string = form.string.data
            coupon.type = form.type.data
            coupon.value = form.value.data
            coupon.update()

            flash(notify_success("Coupon updated!"))
            return mhelp.redirect_url("shopman.coupon", store_id=coupon.coupon_store.id)
        else:
            flash_errors(form)
            return mhelp.redirect_url("shopman.coupon", store_id=coupon.coupon_store.id)


@module_blueprint.route("/s/<store_id>/order/dashboard", methods=["GET", "POST"])
@login_required
def order(store_id):
    order_items = OrderItem.query.filter(OrderItem.store_id == store_id)
    context = mhelp.context()
    context.update({"dir": dir, "order_items": order_items, "get_product": get_product, 'store_id': store_id})
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id)})
    return mhelp.render("order.html", **context)

@module_blueprint.route("/s/<store_id>/order_item/<item_id>/view/dashboard", methods=["GET", "POST"])
@login_required
def order_view(store_id, item_id):
    order_item = OrderItem.query.get(item_id)
    context = mhelp.context()
    context.update({"order_item": order_item, "get_product": get_product, 'store_id': store_id})
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id)})
    return mhelp.render("order_item_view.html", **context)


@module_blueprint.route("/s/<store_id>/order_item/<item_id>/status", methods=["POST"])
@login_required
def order_status_change_seller(store_id, item_id):
    if request.method == 'POST':
        order_status = request.form['order_status']
        order_item = OrderItem.query.get(item_id)
        valid_status = ['pending', 'processing', 'shipped', 'cancelled', 'refunded']
        if order_status not in valid_status:
            return 'unknown order status'
        order_item.status = order_status
        order_item.update()
        flash(notify_success('Order Updated'))
        return mhelp.redirect_url('shopman.order_view', store_id=store_id, item_id=item_id)



@module_blueprint.route("/order/<order_id>/delete", methods=["GET", "POST"])
@login_required
def order_delete(order_id):
    order = Order.query.get(order_id)
    store_id = order.order_store.id
    order.delete()
    return mhelp.redirect_url("shopman.order", store_id=store_id)


@module_blueprint.route("/s/<store_id>/product/list/dashboard")
@login_required
def product_list_dashboard(store_id):
    context = mhelp.context()
    store = Store.query.get(store_id)
    products = store.products
    context.update({'products': products, "store_id": store_id})
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id)})
    return mhelp.render("product_list.html", **context)


@module_blueprint.route("/s/<store_id>/product/<product_id>/view/dashboard")
@login_required
def product_view_dashboard(store_id, product_id):
    context = mhelp.context()
    product = Product.query.get(product_id)
    context.update({'product': product, "store_id": store_id})
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id)})
    return mhelp.render("product_view.html", **context)


@module_blueprint.route("/s/<store_id>/product/<product_id>/status/<status>/return/<return_to>")
@login_required
def set_product_status(store_id, product_id, status, return_to):
    product = Product.query.get(product_id)
    valid_statuses = [
        'pending',
        'not_submitted',
        'approved']
    if status not in valid_statuses:
        return 'error'
    if status == 'pending':
        product.set_status_pending()
    elif status == 'not_submitted':
        product.set_status_not_submitted()
    elif status == 'approved':
        product.set_status_approved()
    else:
        pass
    product.update()
    returns = {
        '1': url_for('shopman.product_view_dashboard', store_id=store_id, product_id=product.id),
    }
    try:
        to_return_url = returns[return_to]
    except KeyError as e:
        return 'error'

    return redirect(to_return_url)

@module_blueprint.route(
    "/s/<store_id>/product/add/category/dashboard", methods=["GET", "POST"]
)
@login_required
def product_add_choose_category_dashboard(store_id):
    context = mhelp.context()
    categories = Category.query.all()
    context.update({
        '_hide_nav': True, 
        '_logout_url':url_for('store.logout', store_id=store_id),
        'categories': categories,
        "store_id": store_id
        })
    return mhelp.render("product_add_choose_category.html", **context)


@module_blueprint.route(
    "/s/<store_id>/product/add/c/<category_id>/subcategory/dashboard", methods=["GET", "POST"]
)
@login_required
def product_add_choose_subcategory_dashboard(store_id, category_id):
    context = mhelp.context()
    category = Category.query.get(category_id)
    subcategories = category.subcategories
    context.update({
        '_hide_nav': True, 
        '_logout_url':url_for('store.logout', store_id=store_id),
        'subcategories': subcategories,
         "store_id": store_id
        })
    return mhelp.render("product_add_choose_subcategory.html", **context)


@module_blueprint.route(
    "/s/<store_id>/product/sub/<subcategory_id>/add/dashboard", methods=["GET", "POST"]
)
@login_required
def product_add_dashboard(store_id, subcategory_id):
    context = mhelp.context()
    context.update({
        '_hide_nav': True, 
        '_logout_url':url_for('store.logout', store_id=store_id),
        'barcodestr': uuid.uuid1(),
        'subcategory_id': subcategory_id,
         "store_id": store_id
         })
    return mhelp.render("product_add.html", **context)


@module_blueprint.route("/s/<store_id>/product/add/check", methods=["GET", "POST"])
@login_required
def product_add_check(store_id):

    if request.method == "POST":
        barcode = request.form["barcode"]
        name = request.form["name"]
        description = request.form["description"].replace('\n', '<br>')
        date = request.form["date"]
        price = request.form["price"]
        selling_price = request.form["selling_price"]
        in_stock = request.form["in_stock"]
        subcategory_id = request.form["subcategory_id"]
        if request.form["discontinued"] == "True":
            discontinued = True
        else:
            discontinued = False

        # category = Category.query.filter(
        #     Category.name == category_name).first()
        # print(category, category_name, category.name)
        has_product = Product.query.filter(
                (Product.barcode == barcode) &
                (Product.store_id == store_id)
                    ).first()

        if has_product:
            flash(notify_warning('Barcode exists!'))
            return mhelp.redirect_url("shopman.product_add_dashboard")
        if has_product is None:
            p = Product(
                barcode=barcode,
                name=name,
                in_stock=in_stock,
                discontinued=discontinued,
            )
            if description:
                p.description = description.strip()
            if date:
                p.date = date.strip()
            if price:
                p.price = price.strip()
            elif not price.strip():
                p.price = 0
            if selling_price:
                p.selling_price = selling_price.strip()

            # if 'photos[]' not in request.files:
            #     flash(notify_warning('no file part'))
            try:
                if "photos[]" in request.files:
                    files = request.files.getlist("photos[]")
                    for file in files:
                        filename = unique_filename(
                            secure_filename(file.filename)
                        )
                        file.filename = filename
                        productphotos.save(file)
                        p.resources.append(
                            Resource(
                                type="image",
                                filename=filename,
                                category="product_image",
                            )
                        )
            except flask_uploads.UploadNotAllowed as e:
                pass

            store = Store.query.get(store_id)
            p.product_store = store
            subcategory = SubCategory.query.get(subcategory_id)
            p.subcategory = subcategory
            p.insert()
            
            flash(notify_success('Product Added!'))
            return mhelp.redirect_url("shopman.product_list_dashboard", store_id=store_id)

@module_blueprint.route("/s/<store_id>/product/<product_id>/edit/dashboard", methods=["GET", "POST"])
@login_required
def product_edit_dashboard(store_id, product_id):
    context = mhelp.context()

    product = Product.query.get(product_id)

    context.update(
        {"len": len, "product": product,  "store_id": store_id}
    )
    return mhelp.render("product_edit.html", **context)


@module_blueprint.route(
    "/product/update/check", methods=["GET", "POST"]
)
@login_required
def product_update_check():
    # this block is only entered when the form is submitted
    if request.method == "POST":
        product_id = request.form["product_id"]
        barcode = request.form["barcode"]
        old_barcode = request.form["old_barcode"]
        # category = request.form["category"]

        name = request.form["name"]
        description = request.form["description"].replace('\n', '<br>')

        date = request.form["date"]
        price = request.form["price"]
        store_id = request.form['store_id']
        if not price.strip():
            price = 0
        selling_price = request.form["selling_price"]
        in_stock = request.form["in_stock"]
        if request.form["discontinued"] == "True":
            discontinued = True
        else:
            discontinued = False

        p = Product.query.get(product_id)
        p.barcode = barcode
        p.name = name
        p.description = description
        p.date = date
        p.price = price
        p.selling_price = selling_price
        p.in_stock = in_stock
        p.discontinued = discontinued
        # p.category = category
        try:
            if "photos[]" in request.files:

                files = request.files.getlist("photos[]")
                for file in files:
                    filename = unique_filename(secure_filename(file.filename))
                    file.filename = filename
                    productphotos.save(file)
                    p.resources.append(
                        Resource(
                            type="image",
                            filename=filename,
                            category="product_image",
                        )
                    )
        except flask_uploads.UploadNotAllowed as e:
            pass
        p.set_status_pending()
        p.update()
        return mhelp.redirect_url("shopman.product_view_dashboard", store_id=store_id, product_id=p.id)




@module_blueprint.route("/s/<store_id>/product/<barcode>/delete", methods=["GET", "POST"])
@login_required
def product_delete(store_id, barcode):
    
    product = Product.query.filter(
        (Product.barcode == barcode) &
        (Product.store_id == store_id)
        ).first_or_404()

    for resource in product.resources:
        filename = resource.filename
        delete_file(
            os.path.join(
                current_app.config["UPLOADED_PRODUCTPHOTOS_DEST"], filename
            )
        )
    product.delete()
    db.session.commit()
    return mhelp.redirect_url("shopman.product_list_dashboard", store_id=store_id)


@module_blueprint.route("/s/<store_id>/info", methods=["GET", "POST"])
@login_required
def store_info(store_id):
    context = mhelp.context()
    store = Store.query.get(store_id)
    context.update({
        'store': store
        })
    context.update({'_hide_nav': True, '_logout_url':url_for('store.logout', store_id=store_id),
        'store_id': store_id})
    return mhelp.render("store_info.html", **context)

def is_valid_name(name):
    nsname = name.replace(' ', '')
    return nsname.isalpha()

@module_blueprint.route("/s/<store_id>/update/name", methods=["POST"])
@login_required
def store_update_name(store_id):
    if request.method == 'POST':
        name = request.form['store_name'].strip()
        if not name:
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        if not is_valid_name(name):
            flash(notify_warning('Not valid name'))
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        if Store.shop_name_exists(name):
            flash(notify_warning('Name exists'))
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        store = Store.query.get(store_id)
        store.name = name
        store.save()
        flash(notify_success('Name updated'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)


@module_blueprint.route("/s/<store_id>/update/slug", methods=["POST"])
@login_required
def store_update_slug(store_id):
    if request.method == 'POST':
        slug = request.form['store_slug'].strip()
        if not slug:
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        if not Store.is_valid_slug(slug):
            flash(notify_warning('Not valid slug'))
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        if Store.shop_slug_exists(slug):
            flash(notify_warning('Slug exists'))
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        store = Store.query.get(store_id)
        store.slug = slug
        store.save()
        flash(notify_success('Slug updated'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)


@module_blueprint.route("/s/<store_id>/update/location", methods=["POST"])
@login_required
def store_update_location(store_id):
    if request.method == 'POST':
        location = request.form['store_location'].strip()
        if not location:
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        store = Store.query.get(store_id)
        store.location = location
        store.save()
        flash(notify_success('Location updated'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)


@module_blueprint.route("/s/<store_id>/update/owner_address", methods=["POST"])
@login_required
def store_update_owner_address(store_id):
    if request.method == 'POST':
        owner_address = request.form['store_owner_address'].strip()
        if not owner_address:
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        store = Store.query.get(store_id)
        store.owner_address = owner_address
        store.save()
        flash(notify_success('Owner address updated'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)

@module_blueprint.route("/s/<store_id>/update/owner_phone", methods=["POST"])
@login_required
def store_update_owner_phone(store_id):
    if request.method == 'POST':
        owner_phone = request.form['store_owner_phone'].strip()
        if not owner_phone:
            return mhelp.redirect_url('shopman.store_info', store_id=store_id)
        store = Store.query.get(store_id)
        store.owner_phone = owner_phone
        store.save()
        flash(notify_success('Owner phone updated'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)

@module_blueprint.route("/s/<store_id>/update/store_logo", methods=["POST"])
@login_required
def store_update_store_logo(store_id):
    if request.method == 'POST':
        if "storelogo" in request.files:
            file = request.files["storelogo"]
            store = Store.query.get(store_id)
            old_logo_filename = store.logo_filename
            filename = unique_sec_filename(file.filename)
            file.filename = filename
            storelogophotos.save(file)
            store.logo_filename = filename
            store.save()

            if old_logo_filename is not None:
                try:
                    delete_file(
                        os.path.join(
                                current_app.config["UPLOADED_STORELOGOPHOTOS_DEST"], old_logo_filename
                            )
                    )
                except Exception as e:
                    raise e
            
        flash(notify_success('Store logo updated!'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)


@module_blueprint.route("/s/<store_id>/update/store_banner", methods=["POST"])
@login_required
def store_update_store_banner(store_id):
    if request.method == 'POST':
        if "storebanner" in request.files:
            file = request.files["storebanner"]
            store = Store.query.get(store_id)
            old_banner_filename = store.banner_filename
            filename = unique_sec_filename(file.filename)
            file.filename = filename
            storebannerphotos.save(file)
            store.banner_filename = filename
            store.save()

            if old_banner_filename is not None:
                try:
                    delete_file(
                        os.path.join(
                                current_app.config["UPLOADED_STORELOGOPHOTOS_DEST"], old_banner_filename
                            )
                    )
                except Exception as e:
                    raise e
            
        flash(notify_success('Banner logo updated!'))
        return mhelp.redirect_url('shopman.store_info', store_id=store_id)