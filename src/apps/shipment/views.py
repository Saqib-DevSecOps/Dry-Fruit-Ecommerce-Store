from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from rest_framework.utils import json
from src.administration.admins.models import Order
from src.apps.shipment.bll import get_or_refresh_token, create_shiprocket_order


# Shipment Views for Ship Rocket

class ShipmentCreateOrderView(View):
    def post(self, request, pk):
        token = get_or_refresh_token()
        if token:
            order = Order.objects.filter(id=pk)
            order_data = json.dumps({
                "order_id": order.id,
                "order_date": "2019-07-24 11:11",
                "pickup_location": "Jammu",
                "billing_customer_name": order.full_name,
                "billing_address": order.address,
                "billing_city": order.city,
                "billing_pincode": order.postal_code,
                "billing_state": order.state,
                "billing_country": order.country,
                "billing_email": order.client.email,
                "billing_phone": order.contact,

                "shipping_is_billing": True,
                "order_items": [
                    {
                        "name": "Kunai",
                        "sku": "chakra123",
                        "units": 10,
                        "selling_price": "900",
                    }
                ],
                "payment_method": "Prepaid",
                "sub_total": 9000,
                "length": 10,  # in cms
                "breadth": 15,  # in cms
                "height": 20,  # in cms
                "weight": 2.5  # in kks
            })
            response = create_shiprocket_order(token, order_data)

            if response:
                messages.success(request, "Order created for shipment")
                return redirect('')
            else:
                error_message = "Something went wrong"
                if 'errors' in response:
                    error_message = ", ".join(response['errors'].values())
                messages.error(request, error_message)
                return redirect('failure-page-url')
        else:
            return redirect('token-error-page-url')

#
# class ShipmentGetOrder(ListView):
#     template_name = 'admins/shipped_orders.html'
#     queryset = ShipmentOrder.objects.all()
#     paginate_by = 25
#
#     def get_context_data(self, **kwargs):
#         context = super(ShipmentGetOrder, self).get_context_data(**kwargs)
#         _filter = ShipmentOrderFilter(self.request.GET, queryset=ShipmentOrder.objects.filter())
#         context['filter_form'] = _filter.form
#
#         paginator = Paginator(_filter.qs, 25)
#         page_number = self.request.GET.get('page')
#         page_object = paginator.get_page(page_number)
#
#         context['object_list'] = page_object
#         return context
#
#
# class GetSpecificOrderView(View):
#     def get(self, request, pk):
#         token = get_or_refresh_token()
#
#         order_data = get_specific_order(pk, token)
#
#         if order_data:
#             return redirect(reverse('order_success', kwargs={'order_id': pk}))
#         else:
#             return redirect('Something went wrong')
#
#
# class GetAndSaveOrders(View):
#     def get(self, request):
#         try:
#             token = get_or_refresh_token()
#
#             if token:
#                 orders_data = get_all_orders(token)
#
#                 for order_data in orders_data:
#                     # Create ShipmentOrder object
#                     shipment_order, created = ShipmentOrder.objects.update_or_create(
#                         id=order_data['id'],
#                         defaults={
#                             'channel_id': order_data['channel_id'],
#                             'channel_name': order_data['channel_name'],
#                             'base_channel_code': order_data['base_channel_code'],
#                             'channel_order_id': order_data['channel_order_id'],
#                             'customer_name': order_data['customer_name'],
#                             'customer_email': order_data['customer_email'],
#                             'customer_phone': order_data['customer_phone'],
#                             'customer_address': order_data['customer_address'],
#                             'pickup_location': order_data['pickup_location'],
#                             'payment_status': order_data['payment_status'],
#                             'total': order_data['total'],
#                             'tax': order_data['tax'],
#                             'sla': order_data['sla'],
#                             'shipping_method': order_data['shipping_method'],
#                             'expedited': order_data['expedited'],
#                             'status': order_data['status'],
#                             'status_code': order_data['status_code'],
#                             'payment_method': order_data['payment_method'],
#                             'is_international': order_data['is_international'],
#                             'purpose_of_shipment': order_data['purpose_of_shipment'],
#                             'channel_created_at': order_data['channel_created_at'],
#                             'created_at': order_data['created_at'],
#                         }
#                     )
#
#                     # Create ShipmentProduct objects
#                     products_data = order_data.get('products', [])
#                     for product_data in products_data:
#                         ShipmentProduct.objects.create(
#                             order=shipment_order,
#                             id=product_data['id'],
#                             channel_order_product_id=product_data['channel_order_product_id'],
#                             name=product_data['name'],
#                             channel_sku=product_data['channel_sku'],
#                             quantity=product_data['quantity'],
#                             product_id=product_data['product_id'],
#                             available=product_data['available'],
#                             status=product_data['status'],
#                             hsn=product_data['hsn'],
#                         )
#
#                     # Create ShipmentDetail objects
#                     shipments_data = order_data.get('shipments', [])
#                     for shipment_data in shipments_data:
#                         ShipmentDetail.objects.create(
#                             order=shipment_order,
#                             id=shipment_data['id'],
#                             isd_code=shipment_data['isd_code'],
#                             courier=shipment_data['courier'],
#                             weight=shipment_data['weight'],
#                             dimensions=shipment_data['dimensions'],
#                             pickup_scheduled_date=shipment_data['pickup_scheduled_date'],
#                             pickup_token_number=shipment_data['pickup_token_number'],
#                             awb=shipment_data['awb'],
#                             return_awb=shipment_data['return_awb'],
#                             volumetric_weight=shipment_data['volumetric_weight'],
#                             pod=shipment_data['pod'],
#                             etd=shipment_data['etd'],
#                             rto_delivered_date=shipment_data['rto_delivered_date'],
#                             delivered_date=shipment_data['delivered_date'],
#                             etd_escalation_btn=shipment_data['etd_escalation_btn'],
#                         )
#
#                 return redirect('success-url')
#             else:
#                 return redirect('failure-url')
#
#         except Exception as e:
#             return redirect('error-url')
