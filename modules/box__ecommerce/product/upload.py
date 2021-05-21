from app import app

from modules.box__ecommerce.product.models import ProductApprovalChoices
from shopyoapi.init import db


def upload_product_approval_choices():
    with app.app_context():
        texts = [
            'incomplete description',
            'nudity, violence and similar',
            'image needs clarity',
            'description needs clarity'
        ]
        for t in texts:
            pac = ProductApprovalChoices(
                text=t
            )
            pac.save(commit=False)
        db.session.commit()


def upload():
    print('Adding product approval messages ...')
    upload_product_approval_choices()
