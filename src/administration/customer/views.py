from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from src.administration.admins.models import OrderItem, Order, Cart
from src.administration.customer.serializer import OrderItemSerializer, OrderSerializer


# Create your views here.
class PurchasedItemListAPIView(generics.ListAPIView):
    """
    Purchased Item List API View.

    # Description:
    This API view returns a list of purchased items for the authenticated user.

    # Endpoint:
        /api/purchased-items/
    # HTTP Methods:
     GET
    # Permission:
     IsAuthenticated

    # Response:
        - 200 OK: Returns the list of purchased items for the user.
        - 401 Unauthorized: If the user is not authenticated.

    # Used Serializers:
        - OrderItemSerializer

    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        order_items = OrderItem.objects.filter(order__user=user)
        return order_items


class OrderCreateAPIView(generics.CreateAPIView):
    """
       Order Create API View.

       # Description:
       This API view allows authenticated users to create an order by providing the necessary details and transferring
       the items from their cart to the order.

       # Endpoint:
            /api/orders/
       # HTTP Methods:
        POST
       # Permission:
        IsAuthenticated

       # Request Body:
            - name: String field for the billing name.
            - street_address: String field for the street address.
            - postal_code: String field for the postal code.
            - city: String field for the city.
            - country: String field for the country.
            - phone: String field for the phone number.
            - email: String field for the email address.

       # Response:
            - 201 Created: Returns the created order details.
            - 400 Bad Request: If the request data is invalid.
            - 401 Unauthorized: If the user is not authenticated.

       # Used Serializers:
            - OrderSerializer

       """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        user = self.request.user

        # Get billing information from request data
        name = self.request.data.get('name')
        street_address = self.request.data.get('street_address')
        postal_code = self.request.data.get('postal_code')
        city = self.request.data.get('city')
        country = self.request.data.get('country')
        phone = self.request.data.get('phone')
        email = self.request.data.get('email')

        # Calculate total amount
        total = 0
        cart_items = Cart.objects.filter(user=user)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity

        # Create the order
        order = Order.objects.create(
            user=user,
            name=name,
            street_address=street_address,
            postal_code=postal_code,
            city=city,
            country=country,
            phone=phone,
            email=email,
            total=total
        )

        # Create order items from cart items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                qty=cart_item.quantity
            )

        # Clear the cart
        cart_items.delete()

        serializer.instance = order


class OrderDetailAPIView(generics.RetrieveAPIView):
    """
       Order Detail API View.

       # Description:
       This API view returns the details of a specific order for the authenticated user.

       # Endpoint:
            /api/orders/<order_id>/
       # HTTP Methods:
        GET
       # Permission:
        IsAuthenticated

       # Response:
            - 200 OK: Returns the details of the specified order.
            - 401 Unauthorized: If the user is not authenticated.
            - 404 Not Found: If the specified order does not exist or does not belong to the user.

       # Used Serializers:
            - OrderSerializer

       """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)

