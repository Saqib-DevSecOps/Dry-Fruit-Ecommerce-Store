import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, MinLengthValidator, \
    MaxLengthValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from phonenumber_field.formfields import PhoneNumberField
from tinymce.models import HTMLField

from src.accounts.models import User
from faker import Faker
from django.utils.translation import gettext_lazy as _

fake = Faker()

""" INVENTORY """


def positive_validator(value):
    if value < 0:
        raise ValidationError('Value must be positive')


def discount_validator(value):
    if value < 0 or value > 100:
        raise ValidationError('Value must be between 0 and 100')


def quantity_validator(value):
    if value < 1 or value > 1000:
        raise ValidationError('Value must be greater than 0')


class Language(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Product Tags"

    def __str__(self):
        return self.tag.name


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    thumbnail_image = models.ImageField(
        upload_to='vendor/inventory/product_category/thumbnail', null=True, blank=True,
        help_text='125*125 thumbnail image in png,jpg or jpeg format'
    )
    banner_image = models.ImageField(
        upload_to='vendor/inventory/product_category/banner', null=True, blank=True,
        help_text='1024*762 thumbnail image in png,jpg or jpeg format'
    )
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Weight(models.Model):
    name = models.CharField(max_length=255, help_text="Product Size Like 1KG etc")
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    PROMOTIONAL_CHOICE = (
        ('new', 'New'),
        ('hot', 'Hot'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(
        help_text="stock-keeping unit (SKU) is a store or catalog's product and service identification code",
        max_length=255
    )
    thumbnail_image = models.ImageField(
        help_text="Thumbnail image for your product tis image will be visible on marketplace",
        upload_to='vendor/inventory/product/thumbnail', null=True, blank=False)

    title = models.CharField(max_length=255, help_text="Product name or title")
    manufacturer_brand = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(blank=True, null=False, unique=False, )
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, through='ProductTag')
    description = HTMLField()
    video_link = models.URLField(null=True, blank=True)

    promotional = models.CharField(max_length=50, choices=PROMOTIONAL_CHOICE, null=True, blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[positive_validator])
    quantity = models.PositiveIntegerField(default=1, help_text="Total quantity of product",
                                           validators=[quantity_validator])
    discount = models.PositiveIntegerField(default=0, verbose_name="Discount in %", help_text="discount  in percentage",
                                           validators=[discount_validator])
    # Statistics
    total_views = models.PositiveIntegerField(default=0)
    total_sales = models.PositiveIntegerField(default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    average_review = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Products"

    def __str__(self):
        return self.title

    def get_tags(self):
        return self.tags.all()

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

    def delete(self, *args, **kwargs):
        self.thumbnail_image.delete(save=True)
        super(Product, self).delete(*args, **kwargs)

    def get_images(self):
        return ProductImage.objects.filter(product=self)

    def get_product_weight(self):
        return ProductWeight.objects.filter(product=self)

    def require_weight(self):
        return ProductWeight.objects.filter(product=self).exists()

    def get_price(self):
        if self.discount > 0:
            return self.price - (self.price * self.discount / 100)
        return self.price

    def total_revenue_generated(self):
        return self.total_sales * self.get_price()

    def get_related_products(self):
        return Product.objects.filter(category=self.category, is_active=True, is_listed=True).exclude(id=self.id)[:10]

    def get_all_ratings(self):
        return ProductRating.objects.filter(product=self)


class ProductWeight(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=False)
    weight = models.ForeignKey(Weight, on_delete=models.SET_NULL, null=True, blank=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[positive_validator])

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.price)

    def get_product_weight_discounted_price(self):
        return self.price * self.product.discount / 100


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to='vendor/inventory/product/images')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']
        verbose_name_plural = "Product Images"

    def __str__(self):
        return self.product.title

    def delete(self, *args, **kwargs):
        self.image.delete(save=True)
        super(ProductImage, self).delete(*args, **kwargs)


class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=False)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=False)
    rate = models.SmallIntegerField(default=1)
    comment = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Product Rating"

    def __str__(self):
        return self.product.title


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_set")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_weight = models.ForeignKey(ProductWeight, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_item_price(self):
        if self.product_weight:
            return self.quantity * self.product_weight.price
        return self.quantity * self.product.get_price()

    def get_discount_price(self):
        if self.product_weight:
            return self.product_weight.get_product_weight_discounted_price() * self.quantity
        return self.quantity * self.product.get_price()


""" ORDERS """

""" ORDER """
ORDER_STATUS_CHOICE = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('cancelled', 'cancelled'),
    ('delivery', 'Delivery'),
    ('completed', 'Completed'),
)
PAYMENT_STATUS_CHOICE = (
    ('unpaid', 'Un Paid'),
    ('pending', 'Pending'),
    ('cancel', 'Cancelled'),
    ('paid', 'Paid'),
    ('refunded', 'Refunded')
)
PAYMENT_TYPE_CHOICE = (
    ('online', 'Online'),
    ('cod', 'Cash on Delivery'),
)
SHIPMENT_STATUS_CHOICE = (
    ('initialized', 'Initialized'),
    ('pending', 'Pending'),
    ('cancelled', 'cancelled'),
    ('delivery', 'Delivery'),
    ('completed', 'Completed'),
)
SHIPMENT_TYPE_CHOICE = (
    ('not-selected', 'Not Selected'),
    ('custom', 'Custom'),
    ('ship_rocket', 'Ship Rocket'),
)

Country = (
    ('USA', 'USA'),
    ('Canada', 'Canada'),
    ('india', 'India'),
)


def validate_contact(value):
    if not value.isdigit() or len(value) != 10 or value[0] not in ['9', '8', '7', '6']:
        raise ValidationError(
            _('Invalid contact number. It should be 10 digits and start with 9/8/7/6.'),
            code='invalid_contact'
        )


class Order(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255, null=True, blank=True)
    contact = models.CharField(max_length=100, null=True, blank=False, validators=[validate_contact])
    postal_code = models.IntegerField(
        null=True,
        blank=False,
        validators=[
            MinValueValidator(100000, message='The pin code must be 6 digits.'),
            MaxValueValidator(999999, message='The pin code must be 6 digits.')
        ]
    )
    address = models.CharField(
        max_length=300,
        null=True,
        blank=False,
        validators=[
            MinLengthValidator(10, message='The address must be at least 10 characters long.'),
            MaxLengthValidator(300, message='The address must be at most 300 characters long.')
        ]
    )
    city = models.CharField(max_length=1000, null=True, blank=False)
    state = models.CharField(max_length=1000, null=True, blank=False)
    country = models.CharField(choices=Country, null=True, blank=False, max_length=20)

    razorpay_order_id = models.CharField(max_length=1000, null=True, blank=True)

    total = models.FloatField(default=0)
    service_charges = models.FloatField(default=0)
    shipping_charges = models.FloatField(default=0)
    sub_total = models.FloatField(default=0)

    payment_type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICE, default=PAYMENT_TYPE_CHOICE[0][0])
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICE, default=ORDER_STATUS_CHOICE[0][0])
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICE, default=PAYMENT_STATUS_CHOICE[0][0])

    shipment_type = models.CharField(max_length=100, choices=SHIPMENT_TYPE_CHOICE, default=SHIPMENT_TYPE_CHOICE[0][0],
                                     null=True,
                                     blank=True)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = "Orders"

    def __str__(self):
        return str(self.pk)

    def get_cart(self):
        return OrderItem.objects.filter(order=self)

    def get_shipment_id(self):
        shipment, created = Shipment.objects.get_or_create(order=self)
        if created:
            shipment.save()
            return shipment.id
        return shipment.id

    def is_online(self):
        return True if self.payment_type == 'online' else False

    def get_shiprocket_shipment_id(self):
        shipment = ShipRocketOrder.objects.filter(order=self).first()
        if shipment:
            return shipment.id
        return None


PAYMENT_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('refunded', 'Refunded'),
    ('cancelled', 'Cancelled'),
]


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    razorpay_payment_id = models.CharField(max_length=1000, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=1000, null=True, blank=True)
    razorpay_signature_id = models.CharField(max_length=1000, null=True, blank=True)

    amount_paid = models.FloatField(default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order.full_name


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_weight = models.ForeignKey(ProductWeight, on_delete=models.SET_NULL, null=True, blank=True)
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order} {self.product.title}."

    def get_total_price(self):
        if self.product_weight:
            return self.product_weight.get_product_weight_discounted_price() * self.qty
        return self.qty * self.product.get_price()


class Shipment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    provider = models.CharField(max_length=250, null=True, blank=False)

    tracking_id = models.CharField(max_length=250, null=True, blank=True)
    tracking_url = models.URLField(null=True, blank=True)
    tracking_number = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(default="*", null=True, blank=False)
    shipment_status = models.CharField(choices=SHIPMENT_STATUS_CHOICE, max_length=20,
                                       default=SHIPMENT_STATUS_CHOICE[0][0])

    started = models.DateTimeField(null=True, blank=True)
    reached = models.DateTimeField(null=True, blank=True)
    shipment_added = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shipment_status

    def save(self, *args, **kwargs):

        # WHEN ASSIGN DELIVERY STATUS, SET STARTED TIME
        if self.shipment_status == 'delivery':
            self.started = timezone.now()

        # WHEN ASSIGN COMPLETED STATUS, SET REACHED TIME
        elif self.shipment_status == 'completed':
            self.reached = timezone.now()

        super(Shipment, self).save(*args, **kwargs)


class BlogCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    thumbnail_image = models.ImageField(
        upload_to='vendor/inventory/product_category/thumbnail', null=True, blank=True,
        help_text='125*125 thumbnail image in png,jpg or jpeg format'
    )
    banner_image = models.ImageField(
        upload_to='vendor/inventory/product_category/banner', null=True, blank=True,
        help_text='1024*762 thumbnail image in png,jpg or jpeg format'
    )
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Post Categories'

    def __str__(self):
        return self.name


class Blog(models.Model):
    STATUS = (
        ('draft', "Draft"),
        ('publish', "Publish")
    )

    title = models.CharField(max_length=255, unique=True)
    thumbnail_image = models.ImageField(upload_to='books/images/posts', null=True, blank=True)
    slug = models.SlugField(unique=True, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, blank=False, null=True)
    content = HTMLField()

    read_time = models.PositiveIntegerField(default=0, help_text='read time in minutes')
    visits = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=15, choices=STATUS, default='publish')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User : {self.user.email} and Product {self.product.title}"


class PickupLocation(models.Model):
    pickup_location = models.CharField(max_length=250, help_text="The nickname of the new pickup location")
    name = models.CharField(max_length=250, help_text="The shipper's name.")
    email = models.CharField(max_length=250)
    phone = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    address_2 = models.CharField(max_length=250)
    city = models.CharField(max_length=250)
    state = models.CharField(max_length=250)
    country = models.CharField(max_length=250)
    pin_code = models.CharField(max_length=250)

    def __str__(self):
        return self.pickup_location


class ShipRocketOrder(models.Model):
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True)
    shiprocket_order_id = models.CharField(max_length=250, null=True, blank=True)
    shipment_id = models.CharField(max_length=250, null=True, blank=True)
    status = models.CharField(max_length=250, null=True, blank=True)
    status_code = models.CharField(max_length=250, null=True, blank=True)
    onboarding_completed_now = models.CharField(max_length=250, null=True, blank=True)
    awb_code = models.CharField(max_length=250, null=True, blank=True)
    courier_company_id = models.CharField(max_length=250, null=True, blank=True)
    courier_name = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.order_id
