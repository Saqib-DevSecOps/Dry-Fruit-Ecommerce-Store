from django.db import models


class ShipmentOrder(models.Model):
    id = models.IntegerField(primary_key=True)
    channel_id = models.IntegerField()
    channel_name = models.CharField(max_length=255)
    base_channel_code = models.CharField(max_length=10)
    channel_order_id = models.CharField(max_length=255)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    customer_address = models.CharField(max_length=100)
    pickup_location = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    sla = models.CharField(max_length=50)
    shipping_method = models.CharField(max_length=50)
    expedited = models.IntegerField()
    status = models.CharField(max_length=50)
    status_code = models.IntegerField()
    payment_method = models.CharField(max_length=50)
    is_international = models.IntegerField()
    purpose_of_shipment = models.IntegerField()
    channel_created_at = models.DateTimeField()
    created_at = models.DateTimeField()

    def __str__(self):
        return f"id {self.id}"

    class Meta:
        ordering = ['-created_at']


class ShipmentProduct(models.Model):
    order = models.ForeignKey('ShipmentOrder', related_name='products', on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    channel_order_product_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    channel_sku = models.CharField(max_length=255)
    quantity = models.IntegerField()
    product_id = models.IntegerField()
    available = models.IntegerField()
    status = models.CharField(max_length=50)
    hsn = models.CharField(max_length=50)

    def __str__(self):
        return f"id {self.id}"


class ShipmentDetail(models.Model):
    order = models.ForeignKey('ShipmentOrder', related_name='shipments', on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    isd_code = models.CharField(max_length=10)
    courier = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    dimensions = models.CharField(max_length=50)
    pickup_scheduled_date = models.DateTimeField(null=True)
    pickup_token_number = models.CharField(max_length=255, null=True)
    awb = models.CharField(max_length=255)
    return_awb = models.CharField(max_length=255)
    volumetric_weight = models.DecimalField(max_digits=10, decimal_places=2)
    pod = models.CharField(max_length=255, null=True)
    etd = models.CharField(max_length=50)
    rto_delivered_date = models.DateTimeField()
    delivered_date = models.DateTimeField(null=True)
    etd_escalation_btn = models.BooleanField(default=False)

    def __str__(self):
        return f"id {self.id}"


class ChannelID(models.Model):
    pass
