# from flask import render_template
# from flask import url_for
# from flask import redirect
from flask import flash
from flask import request
from flask import jsonify
from flask import session

from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user
from flask_login import login_required

from modules.box__ecommerce.product.models import Product
from modules.box__default.admin.models import User
from modules.box__default.auth.forms import LoginForm


from .forms import StoreRegisterForm
from .models import Store
from .models import Store

from shopyoapi.init import ma
from shopyoapi.module import ModuleHelp
from shopyoapi.init import idcardphotos
from shopyoapi.init import brnphotos
from shopyoapi.init import addressphotos
from shopyoapi.file import unique_sec_filename


from shopyoapi.html import notify_success
from shopyoapi.html import notify_danger
from shopyoapi.forms import flash_errors



mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]


class ProductSchema(ma.Schema):
    class Meta:
        model = Product
        fields = ('id', "barcode", 'name', 'price')


class StoreSchema(ma.Schema):
    class Meta:
        model = Store
        fields = ('id', 'name', 'products')

    products = ma.Nested(ProductSchema, many=True)


store_schema = StoreSchema(many=True)


@module_blueprint.route("/<slug>")
def index(slug):
    store = Store.query.filter_by(slug=slug).first_or_404()
    if not store.is_verified:
        return 'Not yet verified'
    login_form = LoginForm()
    context = mhelp.context()
    context.update({
        'store': store,
        'login_form': login_form
        })
    return mhelp.render("store.html", **context)

@module_blueprint.route("/<store_id>/login/check", methods=["GET", "POST"])
def login_check(store_id):
    login_form = LoginForm()
    store = Store.query.get(store_id)

    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_hash(password):
            flash(notify_danger("Please check your user id and password"))
            return mhelp.redirect_url(
                "{}.index".format(mhelp.info["module_name"]),
                slug=store.slug
            )
        if not store.store_owner.email == email:
            flash(notify_danger("Please check your user id and password"))
            return mhelp.redirect_url(
                "{}.index".format(mhelp.info["module_name"]),
                slug=store.slug
            )
        login_user(user)
        return mhelp.redirect_url(
                "shopman.dashboard", store_id=store_id
            )

@module_blueprint.route("/<store_id>/logout", methods=["GET", "POST"])
def logout(store_id):
    store = Store.query.get(store_id)
    logout_user()
    return mhelp.redirect_url(
        "{}.index".format(mhelp.info["module_name"]),
        slug=store.slug
    )

@module_blueprint.route("/dashboard")
def dashboard():

    context = mhelp.context()
    return mhelp.render("dashboard.html", **context)


@module_blueprint.route("register", methods=["GET"])
def register():
    context = mhelp.context()
    context.update({
        'register_form': StoreRegisterForm()
        })
    return mhelp.render("register.html", **context)


@module_blueprint.route("/register/check", methods=["GET", "POST"])
def register_check():
    if request.method == "POST":
        form = StoreRegisterForm()
        if not form.validate_on_submit():
            flash_errors(form)
            return mhelp.redirect_url(
                "{}.register".format(mhelp.info["module_name"])
            )
        store = Store()
        form.populate_obj(store)

        if "brn_file" in request.files:
            file = request.files["brn_file"]

            filename = unique_sec_filename(file.filename)
            file.filename = filename
            brnphotos.save(file)
            store.brn_filename = filename

        if "owner_id_card_file" in request.files:
            file = request.files["owner_id_card_file"]

            filename = unique_sec_filename(file.filename)
            file.filename = filename
            idcardphotos.save(file)
            store.owner_id_card_filename = filename

        if "owner_address_file" in request.files:
            file = request.files["owner_address_file"]

            filename = unique_sec_filename(file.filename)
            file.filename = filename
            addressphotos.save(file)
            store.owner_address_filename = filename

        owner = User()
        owner.email = form.email.data
        owner.first_name = form.first_name.data
        owner.last_name = form.last_name.data
        owner.set_hash(form.password.data)
        owner.store = store
        owner.is_store_owner = True
        owner.save()
        flash(notify_success('Store submitted, wait for approval!'))
        return mhelp.redirect_url(
                "{}.register".format(mhelp.info["module_name"])
            )



@module_blueprint.route("<store_id>/set/featured", methods=["GET"])
@login_required
def toggle_featured(store_id):
    if not current_user.is_admin:
        return 'Not allowed'
    store = Store.query.get(store_id)
    if not store.is_featured:
        store.set_featured()
    elif store.is_featured:
        store.unset_featured()
    store.update()
    return mhelp.redirect_self_url(
                'index', slug=store.slug
            )


@module_blueprint.route("/set/product/<product_id>/featured/<int:rt>", methods=["GET"])
@login_required
def toggle_product_featured(product_id, rt=0):
    if not current_user.is_admin:
        return 'Not allowed'
    product = Product.query.get(product_id)
    if not product.is_featured:
        product.set_featured()
    elif product.is_featured:
        product.unset_featured()
    product.update()
    store_slug = product.product_store.slug
    if rt == 0:
        return mhelp.redirect_self_url(
                    'index', slug=store_slug
                )
    elif rt == 1:
        return mhelp.redirect_url(
                    'shop.product', product_id=product_id
                )