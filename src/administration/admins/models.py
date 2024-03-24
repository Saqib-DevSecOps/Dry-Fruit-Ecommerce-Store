import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from tinymce.models import HTMLField

from src.accounts.models import User
from faker import Faker

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
    name = models.CharField(max_length=255, unique=True)

    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']
        verbose_name_plural = 'Categories'

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
    description = models.TextField(null=True, blank=True, help_text="Small description for your project")
    content = HTMLField(null=True, blank=True, help_text="Full description for your project")
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
        default=5,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )

    # SHIPMENT
    height = models.FloatField(
        null=True, blank=True, validators=[positive_validator], help_text="measurement in inches"
    )
    width = models.FloatField(
        null=True, blank=True, validators=[positive_validator], help_text="measurement in inches"
    )
    length = models.FloatField(
        null=True, blank=True, validators=[positive_validator], help_text="measurement in inches"
    )
    weight = models.FloatField(
        null=True, blank=True, validators=[positive_validator], help_text="weight in grams"
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
    quantity = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

    def get_item_price(self):
        return self.quantity * self.product.price


""" ORDERS """


class Order(models.Model):
    PAYMENT_STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    ORDER_STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('shipping', 'Shipping'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    SHIPPING_STATUS_CHOICE = (
        ('Free', 'Free'),
        ('Normal', 'Normal'),
        ('Premium', 'Premium'),
    )
    ORDER_COUNTRY = (
        ('USA', 'USA'),
        ('Canada', 'Canada'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255, choices=ORDER_COUNTRY)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    total = models.FloatField(default=0)
    paid = models.FloatField(default=0)

    shipping = models.CharField(max_length=15, choices=SHIPPING_STATUS_CHOICE, default='Free')
    stripe_payment_id = models.CharField(max_length=1000, null=True, blank=True)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICE, default='pending')
    order_status = models.CharField(max_length=15, choices=ORDER_STATUS_CHOICE, default='pending')

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.user.name_or_username()} ordered."

    def order_items(self):
        return OrderItem.objects.filter(order=self)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order} {self.product.title}."


class BlogCategory(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

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
