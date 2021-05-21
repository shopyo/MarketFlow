"""Factories to help in dummy uploads."""

from factory import Sequence
from factory.alchemy import SQLAlchemyModelFactory
from factory.fuzzy import FuzzyDecimal
from factory.fuzzy import FuzzyText


from shopyoapi.init import db
from modules.box__ecommerce.store.models import Store
from modules.box__ecommerce.product.models import Product
from modules.box__ecommerce.category.models import Category
from modules.box__ecommerce.category.models import SubCategory

MIN_PRICE = 50
MAX_PRICE = 1000


class BaseFactory(SQLAlchemyModelFactory):
    """Base factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = db.session


class StoreFactory(BaseFactory):
    """Store factory."""

    name = Sequence(lambda n: f"STORE-NAME-{n}")
    brn = Sequence(lambda n: f"BUSSINESS-REG-{n}")
    slug = Sequence(lambda n: f"STORE-SLUG-{n}")
    location = Sequence(lambda n: f"STORE-LOCATION-{n}")
    is_verified = True
    owner_id_card = FuzzyText()
    owner_address = Sequence(lambda n: f"OWNER-ADDRESS-{n}")
    owner_phone = FuzzyText(chars=[str(i) for i in range(10)], length=10)
    is_featured = True

    class Meta:
        """Factory configuration."""

        model = Store


class ProductFactory(BaseFactory):
    """Product factory."""

    barcode = Sequence(lambda n: f"PRODUCT-BARCODE-{n}")
    name = Sequence(lambda n: f"PRODUCT-NAME-{n}")
    price = FuzzyDecimal(MIN_PRICE, MAX_PRICE)
    in_stock = 50
    selling_price = FuzzyDecimal(MIN_PRICE, MAX_PRICE)
    discontinued = False
    description = "PRODUCT DESCRIPTION GOES HERE"
    is_featured = True
    status = "approved"

    class Meta:
        """Factory configuration."""

        model = Product


class CategoryFactory(BaseFactory):
    """Category factory."""

    name = Sequence(lambda n: f"CATEGORY-NAME-{n}")

    class Meta:
        """Factory configuration."""

        model = Category


class SubCategoryFactory(BaseFactory):
    """Category factory."""

    name = Sequence(lambda n: f"SUBCATEGORY-NAME-{n}")

    class Meta:
        """Factory configuration."""

        model = SubCategory


# class UserFactory(BaseFactory):
#     """USER factory."""

#     email = Sequence(lambda n: f"store{n}store.com")
#     is_store_owner = True

#     class Meta:
#         """Factory configuration."""

#         model = User
