# in admin.py

from django.contrib import admin
from .models import Language, Tag, ProductTag, ProductCategory, Product, ProductImage, ProductRating, Cart, Order, \
    OrderItem, BlogCategory, Blog, Wishlist, BillingAddress, ShippingAddress, OrderBillingAddress, OrderShippingAddress, \
    ProductWeight, Weight

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
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(BillingAddress)
class BillingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line1', 'city', 'state', 'postal_code', 'country')
    list_filter = ('user', 'country')


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address_line1', 'city', 'state', 'postal_code', 'country')
    list_filter = ('user', 'country')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'paid', 'shipping', 'payment_status', 'order_status', 'created_on', 'updated_on')
    list_filter = ('user', 'payment_status', 'order_status', 'created_on', 'updated_on')
    search_fields = ('user__username',)
    inlines = [OrderItemInline]


@admin.register(OrderBillingAddress)
class OrderBillingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'address_line1', 'city', 'state', 'postal_code', 'country')
    list_filter = ('user', 'order__created_on', 'country')
    search_fields = ('user__username',)


@admin.register(OrderShippingAddress)
class OrderShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'address_line1', 'city', 'state', 'postal_code', 'country')
    list_filter = ('user', 'order__created_on', 'country')
    search_fields = ('user__username',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Blog)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(Weight)
admin.site.register(ProductWeight)
