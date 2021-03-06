import datetime
import uuid

from werkzeug.security import generate_password_hash

from app import app
from shopyoapi.init import db
from modules.box__default.admin.models import User
from modules.box__default.settings.models import Settings


def add_admin(email, password):
    with app.app_context():
        user = User()
        user.email = email
        user.password = generate_password_hash(password, method="sha256")
        user.is_admin = True
        user.email_confirmed = True
        user.email_confirm_date = datetime.datetime.now()
        user.save()

def add_non_admin(email, password):
    with app.app_context():
        user = User()
        user.email = email
        user.password = generate_password_hash(password, method="sha256")
        user.is_admin = False
        user.email_confirmed = True
        user.email_confirm_date = datetime.datetime.now()
        user.save()


def add_setting(name, value):
    with app.app_context():
        if Settings.query.filter_by(setting=name).first():
            s = Settings.query.get(name)
            s.value = value
            db.session.commit()
        else:
            s = Settings(setting=name, value=value)
            db.session.add(s)
            db.session.commit()
