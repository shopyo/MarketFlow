import json
import os

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user
from flask_login import current_user

from shopyoapi.html import notify_danger
from shopyoapi.html import notify_success

from modules.box__default.admin.models import User
from modules.box__default.auth.forms import LoginForm

dirpath = os.path.dirname(os.path.abspath(__file__))
module_info = {}

with open(dirpath + "/info.json") as f:
    module_info = json.load(f)

auth_blueprint = Blueprint(
    "auth",
    __name__,
    url_prefix=module_info["url_prefix"],
    template_folder="templates",
)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    context = {}
    login_form = LoginForm()
    context["form"] = login_form
    if login_form.validate_on_submit():
        email = login_form.email.data
        password = login_form.password.data
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_hash(password):
            flash(notify_danger("please check your user id and password"))
            return redirect(url_for("www.index"))
        login_user(user)
        if user.is_admin:
            flash(notify_success('Successfully logged in!'))
            return redirect(url_for("dashboard.index"))
        elif user.is_store_owner:
            flash(notify_success('Successfully logged in!'))
            store_id = user.store.id
            return redirect(url_for("shopman.dashboard", store_id=store_id))
        elif user.is_customer:
            flash(notify_success('Successfully logged in!'))
            return redirect(url_for("shop.homepage"))

    return render_template("auth/login.html", **context)


@auth_blueprint.route("/shop", methods=["GET", "POST"])
def shop_login():
    context = {}
    login_form = LoginForm()
    context["form"] = login_form
    if request.method == "POST":
        if login_form.validate_on_submit():
            email = login_form.email.data
            password = login_form.password.data
            user = User.query.filter_by(email=email).first()
            if user is None or not user.check_hash(password):
                flash(notify_danger("please check your user id and password"))
                return redirect(url_for("shop.checkout"))
            login_user(user)
            return redirect(url_for("shop.checkout"))
    return render_template("auth/shop_login.html", **context)


@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash(notify_success("Successfully logged out"))
    return redirect(url_for("auth.login"))
