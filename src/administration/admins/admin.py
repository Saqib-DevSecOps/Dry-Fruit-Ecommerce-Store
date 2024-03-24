# in admin.py

from django.contrib import admin
from .models import Language, Tag, ProductTag, ProductCategory, Product, ProductImage, ProductRating, Cart, Order, \
    OrderItem, BlogCategory, Blog, Wishlist

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
            'sku', 'thumbnail_image', 'title', 'manufacturer_brand', 'slug', 'category', 'description', 'content',
            'video_link')
        }),
        ('Price & Inventory', {
            'fields': ('price', 'quantity', 'discount', 'promotional')
        }),
        ('Statistics', {
            'fields': ('total_views', 'total_sales', 'total_reviews', 'average_review')
        }),
        ('Shipment', {
            'fields': ('height', 'width', 'length', 'weight')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = (
        'user', 'name', 'street_address', 'city', 'country', 'total', 'paid', 'shipping', 'payment_status',
        'order_status',
        'created_on')
    search_fields = ['user__username', 'name', 'street_address', 'city', 'country']
    list_filter = ['shipping', 'payment_status', 'order_status']
    readonly_fields = ('total',)
    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'street_address', 'postal_code', 'city', 'country', 'phone', 'email')
        }),
        ('Payment', {
            'fields': ('total', 'paid', 'stripe_payment_id', 'payment_status')
        }),
        ('Order', {
            'fields': ('shipping', 'order_status')
        }),
        ('Timestamps', {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Blog)
admin.site.register(Wishlist)
admin.site.register(Cart)
