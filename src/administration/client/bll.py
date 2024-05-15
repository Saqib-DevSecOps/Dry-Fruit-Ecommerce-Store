from src.administration.admins.models import Product


def calculate_reviews(rate, product_id):
    product = Product.objects.get(id=product_id)
    product.average_review = (rate + product.average_review) / (1 + product.total_reviews)
    product.total_reviews += 1
    product.save()

