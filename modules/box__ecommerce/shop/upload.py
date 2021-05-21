import os
import json

from app import app

from userapi.path import get_boxpath
from shopyoapi.enhance import get_setting
from  shopyoapi.init import db

from modules.box__ecommerce.shop.models import Currency
from modules.box__ecommerce.shop.models import Country
from modules.box__ecommerce.shop.models import CitySublocality

def upload_currency():
    with open(
        os.path.join(
            get_boxpath(__file__),
            "shop",
            "data",
            "currency.json",
        )
    ) as f:
        currencies = json.load(f)
    with app.app_context():
        for curr in currencies:
            c = Currency()
            c.cc = curr['cc']
            c.symbol = curr['cc']
            c.name = curr['name']
            c.save(commit=False)
        db.session.commit()

def upload_country():
    with open(
        os.path.join(
            get_boxpath(__file__),
            "shop",
            "data",
            "country.json",
        )
    ) as f:
        countries = json.load(f)
    with app.app_context():
        for country in countries:
            c = Country()
            c.name = country['name']
            c.code = country['code']
            c.save(commit=False)
        db.session.commit()


def title_string(string):
    if string is None or string.strip() == '':
        return string
    else:
        return string.title()
def upload_city_sublocality():
    with open(
        os.path.join(
            get_boxpath(__file__),
            "shop",
            "data",
            "city_sublocality.json",
        )
    ) as f:
        cities_sublocalities = json.load(f)
    with app.app_context():
        for key in cities_sublocalities:
            for sublocality in cities_sublocalities[key]:
                c = CitySublocality()
                c.locality = title_string(key)
                c.sublocality = title_string(sublocality['name'])
                c.code = title_string(sublocality['code'])
                c.street = title_string(sublocality['street'])
                c.save(commit=False)
        db.session.commit()

def upload():
    print('Adding currency ...')
    upload_currency()

    print('Adding country ...')
    upload_country()

    print('Adding city sublocality')
    upload_city_sublocality()

