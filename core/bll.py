import decimal

from django.utils import timezone


def calculate_shipping_charges(total):
    return 0


def calculate_service_charges(total):
    # 6.5% of total amount
    if total > 0:
        return total * 0.065
    return 0


def calculate_product_listening_charges():
    return 0


def calculate_sale_service_charges(amount):
    return 0


def convert_cents_to_decimal(amount_in_cents):
    return decimal.Decimal(amount_in_cents) / 100


def get_listing_charges():
    return 0.20


def get_listing_days(start_date_time):
    return start_date_time + timezone.timedelta(days=30)


def get_payment_processing_fee(amount):
    # 4% of total amount
    if amount > 0:
        return amount * 0.04
    return 0
