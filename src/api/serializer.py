from rest_framework import serializers

from src.accounts.models import User
from src.administration.admins.models import Product, Cart, BlogCategory, Blog, Order, OrderItem, Wishlist, Tag, \
    ProductTag, ProductCategory, ProductImage, ProductRating


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=250, source='get_full_name')

    class Meta:
        model = User
        fields = ['profile_image', 'full_name']


class ProductTagSerializer(serializers.ModelSerializer):
    tag = TagSerializer()

    class Meta:
        model = ProductTag
        fields = ['id', 'name']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'thumbnail_image', 'banner_image']


class ProductListSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = ['id', 'sku', 'title', 'category', 'slug', 'quantity', 'thumbnail_image', 'price', 'discount',
                  'promotional',
                  'total_reviews', 'average_review', ]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductReviewsSerializer(serializers.ModelSerializer):
    client = UserSerializer()

    class Meta:
        model = ProductRating
        fields = [
            'client', 'product__total_reviews', 'product__average_review', 'rate', 'comment', 'created_on'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    tags = TagSerializer(many=True)
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'title', 'slug', 'manufacturer_brand', 'category', 'tags', 'images', 'description',
            'thumbnail_image',
            'video_link', 'quantity', 'price', 'discount', 'promotional', 'total_reviews',
        ]


class CartListSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    product = ProductListSerializer()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_weight', 'quantity', 'created_on']


class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'user', 'product', 'product_weight', 'quantity']


class CartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'quantity']


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'created_on', 'updated_on']
        read_only_fields = ['id', 'user', 'created_on', 'updated_on']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'qty']


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total',
                  'paid', 'shipping', 'payment_status', 'order_status', 'created_on',
                  'updated_on']
        read_only_fields = ['id', 'created_on', 'updated_on', 'order_items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)

        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)

        return order
