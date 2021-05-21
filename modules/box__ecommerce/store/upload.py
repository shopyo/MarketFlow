import datetime
import uuid

from app import app
import os
import math

from shopyoapi.init import db
from modules.box__ecommerce.category.upload import add_uncategorised_category
from modules.box__ecommerce.category.upload import add_some_category
from modules.box__ecommerce.product.models import Product
from modules.box__ecommerce.category.models import SubCategory
from modules.box__ecommerce.store.models import Store
from modules.box__default.admin.models import User
from shopyoapi.uploads import add_non_admin
from shopyoapi.file import trycopy
from shopyoapi.path import static_path
from .factories import StoreFactory
from .factories import ProductFactory
from .factories import CategoryFactory
from .factories import SubCategoryFactory


def upload_dummy_store_with_products2():
    with app.app_context():

        subcategories = SubCategory.query.all()
        stores = StoreFactory.create_batch(10)

        for subcategory in subcategories:
            products = ProductFactory.create_batch(33)
            subcategory.products = products
            prod_per_store = int((len(products) / len(stores)))
            subcategory.save(commit=False)

            for i in range(len(stores)):

                if stores[i].products is None:
                    stores[i].products = []

                k = i * prod_per_store

                if i == (len(stores) - 1):
                    stores[i].products.extend(products[k:])
                else:
                    stores[i].products.extend(products[k: k + prod_per_store])
                stores[i].save(commit=False)

        db.session.commit()


def upload_dummy_store_with_products():
    with app.app_context():
        p1 = Product(
                barcode=str(uuid.uuid1()),
                price=10.0,
                name="Apple",
                in_stock=50,
                selling_price=15.0,
                discontinued=False,
                description="",
                is_featured=True
            )
        p2 = Product(
            barcode=str(uuid.uuid1()),
            price=10.0,
            name="Pear",
            in_stock=50,
            selling_price=15.0,
            discontinued=False,
            description="",
        )
        p3 = Product(
            barcode=str(uuid.uuid1()),
            price=10.0,
            name="Peach",
            in_stock=50,
            selling_price=15.0,
            discontinued=False,
            description="",
        )

        sub_uncateg = SubCategory.query.filter(SubCategory.name == 'uncategorised').first()
        p1.subcategory = sub_uncateg
        p1.set_status_approved()
        p2.subcategory = sub_uncateg
        p2.set_status_approved()
        p3.subcategory = sub_uncateg
        p3.set_status_approved()

        store1_logo = 's1_marketflow_logo.png'
        store1_banner = 's1_marketflow_banner.png'
        store = Store(
            name='TM Shop',
            slug='tm-shop',
            brn='1234',
            location='Impasse La Roue, Bonne Mer',
            is_verified=True,
            owner_id_card='J1234',
            owner_address='Rue des fleurs, Moka',
            owner_phone='1234567',
            logo_filename=store1_logo,
            banner_filename=store1_banner,
            is_featured=True
            )
        trycopy(
            os.path.join(static_path, 'default', 'store', 'marketflow_logo.png'),
            os.path.join(static_path, 'uploads', 'store_logo_photos', store1_logo),
            )
        trycopy(
            os.path.join(static_path, 'default', 'store', 'marketflow_banner.png'),
            os.path.join(static_path, 'uploads', 'store_banner_photos', store1_banner),
            )
        add_non_admin('store@store.com', 'pass')
        dummy_owner = User.query.filter(User.email == 'store@store.com').first()
        dummy_owner.is_store_owner = True
        store.store_owner = dummy_owner
        store.products.extend([p1, p2, p3])
        store.save()

        store2_logo = 's2_marketflow_logo.png'
        store2_banner = 's2_marketflow_banner.png'
        store2 = Store(
            name='Talent Moris',
            slug='talent-moris',
            brn='123e4',
            location='Pamplemousses',
            is_verified=True,
            owner_id_card='J1234eee',
            owner_address='Rue des fleurs, Port Louis',
            owner_phone='1237777',
            logo_filename=store2_logo,
            banner_filename=store2_banner,
            is_featured=True
            )
        trycopy(
            os.path.join(static_path, 'default', 'store', 'marketflow_logo.png'),
            os.path.join(static_path, 'uploads', 'store_logo_photos', store2_logo),
            )
        trycopy(
            os.path.join(static_path, 'default', 'store', 'marketflow_banner.png'),
            os.path.join(static_path, 'uploads', 'store_banner_photos', store2_banner),
            )
        descrip = '''
Kick Start Package at : Rs 1500 monthly
Collaborative working space located at Pamplemousses (close to Botanical garden)
Free WIFI
Free meeting spaces
Free parking
Talentmoris.com:
Online store as from MUR 4500 annually
Free delivery

Shared Services at very affordable prices
Administrative & secretarial support: As from MUR 1200 per month
Training – Starting at MUR 1000 monthly
Coaching
Business mentoring
Project management
Business plan
Business development
Legal advice
Printing services
Regular events
        '''.replace('\n', '<br>')
        px = Product(
            barcode=str(uuid.uuid1()),
            price=4500,
            name="Startup Package",
            in_stock=50,
            selling_price=4500,
            discontinued=False,
            description=descrip,
            is_featured=True
        )
        px.set_status_approved()
        px.subcategory = sub_uncateg
        add_non_admin('store@marketflow.com', 'pass')
        dummy_owner2 = User.query.filter(User.email == 'store@marketflow.com').first()
        dummy_owner2.is_store_owner = True
        store2.store_owner = dummy_owner2
        store2.products.extend([px])
        store2.save()


def upload():
    if app.config['DEBUG']:
        print('Uploading dummy store data ...')

        print("Adding category and subcategory uncategorised ...")
        add_uncategorised_category()
        #  print('Adding some more category ...')
        #  add_some_category()
        print('Adding dummy store with products ...')
        upload_dummy_store_with_products2()
