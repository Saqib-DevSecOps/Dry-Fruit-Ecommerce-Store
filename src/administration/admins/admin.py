# in admin.py

from django.contrib import admin
from .models import Language, Tag, ProductTag, ProductCategory, Product, ProductImage, ProductRating, Cart, Order, \
    OrderItem, BlogCategory, Blog, Wishlist, \
    ProductWeight, Weight, Payment, Shipment, PickupLocation, ProductSize, ShipRocketOrder

# Register your models here.

admin.site.register(Language)
admin.site.register(Tag)
admin.site.register(ProductTag)
admin.site.register(ProductCategory)
admin.site.register(ProductRating)
admin.site.register(BlogCategory)


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductTagInline(admin.TabularInline):
    model = ProductTag


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductTagInline]  # Include ProductTagInline here
    list_display = ('title', 'manufacturer_brand', 'category', 'price', 'quantity', 'is_active')
    search_fields = ['title', 'manufacturer_brand']
    list_filter = ['category', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('total_views', 'total_sales', 'total_reviews')
    fieldsets = (
        (None, {
            'fields': (
                'sku', 'thumbnail_image', 'title', 'manufacturer_brand', 'slug', 'category', 'description',
                'video_link')
        }),
        ('Price & Inventory', {
            'fields': ('price', 'quantity', 'discount', 'promotional')
        }),
        ('Statistics', {
            'fields': ('total_views', 'total_sales', 'total_reviews', 'average_review')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['client', 'full_name', 'contact', 'postal_code', 'address', 'city', 'state', 'country', 'total',
                    'service_charges', 'sub_total', 'payment_type', 'order_status', 'payment_status',
                    'created_on']
    list_filter = ['order_status', 'payment_status', 'created_on']
    search_fields = ['client__username', 'full_name', 'contact', 'postal_code', 'address', 'city', 'state', 'country']


class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'provider', 'shipment_status', 'started', 'reached', 'is_active', 'created_on')
    list_filter = ('shipment_status', 'is_active', 'created_on')
    search_fields = ('order__id', 'provider', 'tracking_id', 'tracking_number')


admin.site.register(Shipment, ShipmentAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Product, ProductAdmin)
admin.site.register(Blog)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Weight)
admin.site.register(ProductWeight)
admin.site.register(ProductSize)
admin.site.register(ShipRocketOrder)
admin.site.register(PickupLocation)
