from sqlalchemy import exists
from sqlalchemy.orm import validates

from shopyoapi.init import db
from shopyoapi.models import PkModel
from flask import current_app
from flask import url_for

from shopyoapi.validators import is_valid_slug

class Store(PkModel):
    __tablename__ = "stores"
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    brn = db.Column(db.String(100), unique=True)
    brn_filename = db.Column(db.String(100), unique=True)
    location = db.Column(db.String(100))
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)

    owner_id_card = db.Column(db.String(100), unique=True)
    owner_id_card_filename = db.Column(db.String(100), unique=True)
    owner_address = db.Column(db.String(100), unique=True)
    owner_address_filename = db.Column(db.String(100), unique=True)
    owner_phone = db.Column(db.String(100), unique=True)

    logo_filename = db.Column(db.String(100), unique=True)
    banner_filename = db.Column(db.String(100), unique=True)
    # relationships 
    products = db.relationship(
        "Product", backref="product_store", cascade="all, delete-orphan", lazy=True
    )

    coupons = db.relationship(
        "Coupon", backref="coupon_store", cascade="all, delete-orphan", lazy=True
    )

    order_items = db.relationship(
        "OrderItem", backref="order_item_store", cascade="all, delete-orphan", lazy=True
    )

    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f"Store: {self.name}"

    @validates("name")
    def convert_lower(self, key, value):
        return value.lower()

    @classmethod
    def shop_name_exists(cls, name):
        return db.session.query(
            exists().where(cls.name == name)
        ).scalar()

    @classmethod
    def shop_slug_exists(cls, slug):
        return db.session.query(
            exists().where(cls.slug == slug)
        ).scalar()

    @staticmethod
    def is_valid_slug(slug):
        return is_valid_slug(slug)


    def get_id_card_url(self):
        return url_for('static', filename='uploads/idcard/{}'.format(
            self.owner_id_card_filename))

    def get_brn_url(self):
        return url_for('static', filename='uploads/brn/{}'.format(
            self.brn_filename))

    def get_address_url(self):
        return url_for('static', filename='uploads/address/{}'.format(
            self.owner_address_filename))

    def get_logo_url(self):
        return url_for('static', filename='uploads/store_logo_photos/{}'.format(
            self.logo_filename))

    def get_banner_url(self):
        return url_for('static', filename='uploads/store_banner_photos/{}'.format(
            self.banner_filename))

    def get_store_page_url(self):
        return url_for('store.index', slug=self.slug)

    def set_featured(self):
        self.is_featured = True

    def unset_featured(self):
        self.is_featured = False