from rest_framework import serializers
from src.administration.admins.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'qty']


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'name', 'street_address', 'postal_code', 'city', 'country', 'phone', 'email', 'total',
                  'paid', 'shipping', 'stripe_payment_id', 'payment_status', 'order_status', 'created_on',
                  'updated_on']
        read_only_fields = ['id', 'created_on', 'updated_on', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)

        return order
