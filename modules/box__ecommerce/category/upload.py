import json
import os

from app import app

from modules.box__ecommerce.category.models import Category
from modules.box__ecommerce.category.models import SubCategory

from shopyoapi.init import db
from userapi.path import get_boxpath

def add_uncategorised_category():
    with app.app_context():
        category = Category(name="uncategorised")
        subcategory = SubCategory(name="uncategorised")
        category.subcategories.append(subcategory)
        category.save()

def add_some_category():
    with app.app_context():
        category = Category(name="Home")
        subcategory1 = SubCategory(name="Kitchen")
        subcategory2 = SubCategory(name="Furniture")
        category.subcategories.append(subcategory1)
        category.subcategories.append(subcategory2)
        category.save()

def add_categories():
    with app.app_context():
        with open(
        os.path.join(
                get_boxpath(__file__),
                "category",
                "data",
                "category.json",
            )
        ) as f:
            categories = json.load(f)

        for cat in categories:
            c = Category(name=cat)
            for sub in categories[cat]:
                s = SubCategory(name=sub)
                c.subcategories.append(s)
            c.save(commit=False)

        db.session.commit()

def upload():
    print('Adding categories')
    add_categories()
