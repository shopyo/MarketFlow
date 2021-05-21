from modules.box__ecommerce.product.models import Product


def get_products():
    return Product.query.filter(
    		Product.status == 'approved'
    	).all()


available_everywhere = {
    "get_products": get_products,
}
