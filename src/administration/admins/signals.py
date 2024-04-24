from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from src.administration.admins.bll import create_order_items
from src.administration.admins.models import Order, OrderItem

""" ORDERS, SUB ORDERS, SHIPMENTS """


@receiver(pre_save, sender=Order)
def order_save_pre(sender, instance, **kwargs):
    if instance.payment_type == "cod":
        instance.order_status = "approved"


@receiver(post_save, sender=Order)
def order_save_post(sender, instance, created, **kwargs):
    if created:
        order = create_order_items(order=instance, user_request=instance.client)
        # notify_buyer_on_order_creation(instance)

    # ON ORDER APPROVE
    if instance.order_status == "approved":

        # DECREASE PRODUCT QUANTITY
        order_items = OrderItem.objects.filter(order=instance)
        for order_item in order_items:
            product = order_item.product
            product.quantity -= order_item.qty
            product.save()

        # NOTIFY VENDOR AND BUYER
        # notify_buyer_on_order_approved(instance)
        # notify_vendor_on_order_approved(instance)

    if instance.order_status == "completed":
        pass



#
# @receiver(pre_save, sender=Shipment)
# def shipment_save_pre(sender, instance, **kwargs):
#     if instance.shipment_status == 'delivery' and not instance.started:
#         instance.started = timezone.now()
#
#     elif instance.shipment_status == 'completed' and not instance.reached:
#         instance.reached = timezone.now()
#
#
# @receiver(post_save, sender=Shipment)
# def shipment_save_post(sender, instance, created, **kwargs):
#     if created:
#         pass
#
#     else:
#
#         # NOTIFY USER ABOUT SHIPMENT STATUS CHANGED
#         sub_order = instance.suborder
#         if instance.shipment_status in ['completed', 'delivery']:
#             sub_order.order_status = instance.shipment_status
#             sub_order.save()
#
#
# """ CHARGES AND TRANSACTIONS """
#
#
# @receiver(post_save, sender=Charge)
# def on_charge_save(sender, instance, created, **kwargs):
#     if instance.status == "init":
#
#         wallet = instance.user.get_user_wallet()
#         wallet.outstanding_charges += instance.fee_amount
#         wallet.save()
#
#     elif instance.status == "pending":
#         pass
#
#     else:
#
#         wallet = instance.user.get_user_wallet()
#         wallet.outstanding_charges -= instance.fee_amount
#         wallet.save()
#
#
# @receiver(post_save, sender=Transaction)
# def transaction_save_post(sender, instance, created, **kwargs):
#     if instance.transaction_type in ["deposit", "refund"]:
#         if instance.status == "completed":
#
#             wallet = instance.user.get_user_wallet()
#             wallet.balance_available += instance.amount
#             wallet.save()
#
#             notify_user_on_transaction(instance)
#
#     elif instance.transaction_type in ["withdraw", "charge"]:
#         if instance.status == "completed":
#
#             wallet = instance.user.get_user_wallet()
#             wallet.balance_available -= instance.amount
#             wallet.save()
#
#             notify_user_on_transaction(instance)
#
#
# """ OTHERS """
#
#
# @receiver(post_save, sender=Order)
# def create_payment(sender, instance, created, **kwargs):
#     if created:
#         Payment.objects.create(order=instance)
#
#
# @receiver(post_save, sender=User)
# def create_vendor_wallet(sender, instance, created, **kwargs):
#     if created:
#         Wallet.objects.create(user=instance)
#     Wallet.objects.get_or_create(user=instance)
#
#
# """ PRODUCTS """
#
#
# @receiver(post_save, sender=Product)
# def on_product_save(sender, instance, created, **kwargs):
#     # WHEN PRODUCT CREATED
#     if created:
#         ProductListing.objects.get_or_create(product=instance)
#
#
# @receiver(pre_save, sender=ProductListing)
# def on_product_listing_save_pre(sender, instance, **kwargs):
#     if instance.status == "approved":
#         instance.charges = get_listing_charges()
#         instance.started_on = timezone.now()
#         instance.expires_on = get_listing_days(timezone.now())
#
#
# @receiver(post_save, sender=ProductListing)
# def on_product_listing_save(sender, instance, created, **kwargs):
#     notify_vendor_on_product_listing(instance)
#
#     if instance.status == "approved":
#
#         ProductListingHistory.objects.create(
#             listing=instance, charges=get_listing_charges(), started_on=timezone.now(),
#             expires_on=get_listing_days(timezone.now())
#         )
#         Charge.objects.create(
#             user=instance.product.vendor, fee_amount=instance.charges, fee_type="product_listing_fee", status="init",
#             content_type=ContentType.objects.get_for_model(instance), content_object=instance, object_id=instance.id,
#             description="Product Listing Fee for Product: " + instance.product.title
#         )
#
#     elif instance.status == "applied":
#         pass
#     elif instance.status == "cancelled":
#         pass
#     elif instance.status == "expired":
#         pass
#
#
# @receiver(post_save, sender=ProductListingHistory)
# def on_product_listing_history_save(sender, instance, created, **kwargs):
#     if created and instance.listing.status == "approved":
#         print("Product Listing Fee Added")
#
#
# @receiver(post_save, sender=ProductRating)
# def on_product_rating_save(sender, instance, created, **kwargs):
#     ratings = ProductRating.objects.filter(product=instance.product)
#     total_rating = ratings.count()
#     average_rating = sum([rating.rate for rating in ratings]) / total_rating
#     instance.product.total_reviews = total_rating
#     instance.product.average_review = int(average_rating)
#     instance.product.save()