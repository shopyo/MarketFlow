import datetime

from flask import url_for
from shopyoapi.init import db
from datetime import datetime

# from modules.box__ecommerce.pos.models import Transaction
from modules.resource.models import Resource
from modules.box__ecommerce.store.models import Store
from shopyoapi.models import PkModel

transaction_helpers = db.Table(
    "transaction_helpers",
    db.Column("product_barcode", db.String(100), db.ForeignKey("product.barcode")),
    db.Column("transaction_id", db.Integer, db.ForeignKey("transactions.id")),
)


class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True)
    price = db.Column(db.Float)
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    date = db.Column (db.String(100))
    in_stock = db.Column(db.Integer)
    discontinued = db.Column(db.Boolean)
    selling_price = db.Column(db.Float)
    status = db.Column(db.String(100), default="pending") # not_submitted, pending, approved

    is_onsale = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)

    subcategory_id = db.Column(db.Integer, db.ForeignKey("subcategories.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))

    transactions = db.relationship(
        "Transaction",
        secondary=transaction_helpers,
        backref="products",
        cascade="all, delete",
    )
    resources = db.relationship(
        "Resource", backref="resources", lazy=True, cascade="all, delete"
    )
    moderation_messages = db.relationship(
        "ModerationMessage", backref="message_product", lazy=True, cascade="all, delete"
    )
    order_items = db.relationship(
        "OrderItem", backref="order_item_product", lazy=True, cascade="all, delete"
    )

    def __repr__(self):
        return f"Product: {self.barcode}"

    def add(self):
        db.session.add(self)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def set_status_pending(self):
        self.status = 'pending'

    def set_status_not_submitted(self):
        self.status = 'not_submitted'

    def set_status_approved(self):
        self.status = 'approved'

    def get_one_image_url(self):
        if len(self.resources) == 0:
            return url_for('static', filename='default/default_product.jpg')
        else:
            resource = self.resources[0]
            return url_for('static', filename='uploads/products/{}'.format(resource.filename))

    def get_buy_page_url(self):
        return url_for('shop.product', product_id=self.id)

    def set_featured(self):
        self.is_featured = True

    def unset_featured(self):
        self.is_featured = False

class ProductApprovalChoices(PkModel):
    __tablename__ = "product_approval_choices"
    text = db.Column(db.String(100), unique=True)

class ModerationMessage(PkModel):
    __tablename__ = "moderation_messages"

    text = db.Column(db.String(100), unique=True)
    time = db.Column(db.DateTime, default=datetime.now())

    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))

    def get_std_formatted_time(self):
        return self.time.strftime("%b %d %Y, %H:%M")
