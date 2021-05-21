from shopyoapi.uploads import add_non_admin
from modules.box__default.admin.models import User

from app import app

def add_customer():
    with app.app_context():

        customer = User(
            username='qwert',
            email='cust@gmail.com',
            )
        customer.set_hash('pass')
        customer.is_customer = True
        customer.save()

def upload():
    add_customer()