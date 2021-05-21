from datetime import datetime

from shopyoapi.init import db
from shopyoapi.models import PkModel

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.now())

    logged_in_customer_email = db.Column(db.String(120), default="")

    coupon = db.relationship(
        "Coupon", backref="coupon_order", lazy=True, uselist=False
    )

    order_items = db.relationship(
        "OrderItem",
        backref="item_order",
        lazy=True,
        cascade="all, delete, delete-orphan",
    )
    billing_detail = db.relationship(
        "BillingDetail",
        uselist=False,
        backref="billing_detail_order",
        cascade="all, delete, delete-orphan",
    )

    payment_option_name = db.Column(db.String(120))
    payment_option_text = db.Column(db.String(120))

    shipment_option = db.relationship(
        "DeliveryOption",
        backref="shipment_option_order",
        lazy=True,
        uselist=False,
    )

    payment_option = db.relationship(
        "PaymentOption",
        backref="payment_option_order",
        lazy=True,
        uselist=False,
    )

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

    def get_std_formatted_time(self):
        return self.time.strftime("%b %d %Y, %H:%M")


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.now())
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer)
    status = db.Column(
        db.String(120), default="pending"
    )  # pending, processing, shipped, cancelled, refunded
    # TODO: must be put in table

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

    def set_status_processing(self):
        self.status = 'processing'

    def set_status_shipped(self):
        self.status = 'shipped'

    def set_status_cancelled(self):
        self.status = 'cancelled'

    def set_status_on_hold(self):
        self.status = 'on_hold'

    def set_status_refunded(self):
        self.status = 'refunded'

    def get_chart_time(self):
        return self.time.strftime("%d/%m/%Y %H:%M")



class BillingDetail(db.Model):
    __tablename__ = "billing_details"

    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    country = db.Column(db.String(100))
    street = db.Column(db.String(100))
    town_city = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    email = db.Column(db.String(100))
    order_notes = db.Column(db.String(100))

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

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

class Country(PkModel):
    __tablename__ = "countries"

    name = db.Column(db.String(100))
    code = db.Column(db.String(100))


class Currency(PkModel):
    __tablename__ = "currencies"

    cc = db.Column(db.String(100))
    symbol = db.Column(db.String(100))
    name = db.Column(db.String(100))


class CitySublocality(PkModel):
    __tablename__ = "cities_sublocalities"

    country = db.Column(db.String(100), default="mauritius")
    locality = db.Column(db.String(100))
    sublocality = db.Column(db.String(100))
    code = db.Column(db.String(100))
    street = db.Column(db.String(100))