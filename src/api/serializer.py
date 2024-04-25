from rest_framework import serializers
from src.accounts.models import User
from src.administration.admins.models import ProductCategory, Product, Cart, Wishlist, Order, OrderItem, \
    ProductRating, ProductTag, ProductImage, Tag, Weight, ProductWeight


class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = ['id', 'name']


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'parent', 'thumbnail_image']


""" HOME """


class ProductHomeSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'thumbnail_image', 'price', 'discount', 'category',
        ]


class HomeProductsListSerializer(serializers.Serializer):
    all_products = ProductHomeSerializer(many=True)
    new_products = ProductHomeSerializer(many=True)
    most_sales = ProductHomeSerializer(many=True)
    categories = ProductCategorySerializer(many=True)


""" CART """


class CartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity']

    def validate(self, data):
        user = self.context['request'].user
        product = data['product']
        quantity = data['quantity']

        if not product.is_active:
            raise serializers.ValidationError('Product not available')
        if product.quantity < 1:
            raise serializers.ValidationError('Product out of stock')
        if quantity <= 0:
            raise serializers.ValidationError('Quantity cannot be zero or negative')
        if quantity > product.quantity:
            raise serializers.ValidationError('Quantity limit exceeded')
        if Cart.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError('Product already in cart')

        return data


class CartListSerializer(serializers.ModelSerializer):
    product = ProductHomeSerializer()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity']


class CartUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity']

    def validate(self, data):
        instance = self.instance
        product = instance.product if instance else None
        quantity = data.get('quantity', instance.quantity if instance else None)

        if not instance:
            raise serializers.ValidationError('Product not found in the cart')

        if not product.is_active:
            raise serializers.ValidationError('Product not available')

        if quantity <= 0:
            raise serializers.ValidationError('Quantity cannot be zero or negative')

        if quantity > product.quantity:
            raise serializers.ValidationError('Quantity limit exceeded')

        if product.quantity <= 0:
            raise serializers.ValidationError('Product out of stock')

        return data


""" PRODUCT """


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductWeightSerializer(serializers.ModelSerializer):
    weight = WeightSerializer()

    class Meta:
        model = ProductWeight
        fields = ['id', 'price', 'weight']


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'thumbnail_image',
            'quantity', 'price', 'discount', 'promotional', 'total_reviews',
            'average_review',
            'category',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer()
    # tags = ProductTagSerializer(many=True)
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')
    product_weight = ProductWeightSerializer(many=True, read_only=True, source='get_product_weight')

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'title', 'slug', 'manufacturer_brand', 'category', 'images', 'description',
            'thumbnail_image',
            'video_link', 'quantity', 'price', 'discount', 'promotional', 'total_reviews', 'product_weight'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'title', 'slug', 'description', 'thumbnail_image', 'price',
            'discount', 'promotional', 'total_reviews', 'average_review'
        ]


class ProductsSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteCartItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, data):
        instance = self.instance
        if not instance:
            raise serializers.ValidationError('Product not found in the cart')
        return data


""" WISHLIST """


class WishlistListSerializer(serializers.ModelSerializer):
    product = ProductHomeSerializer()

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_on']


class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product']

    def validate(self, data):
        user = self.context['request'].user
        product = data['product']
        if Product.objects.filter(pk=product.id, is_active=False).exists():
            raise serializers.ValidationError('Product not available')
        if product.quantity <= 0:
            raise serializers.ValidationError('Product out of stock')
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError('Product already in wishlist')
        return data


class WishlistDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product']


""" ORDER """


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer()

    class Meta:
        model = OrderItem
        fields = ['product', 'qty']


class OrderDetailSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='get_cart')

    class Meta:
        model = Order
        fields = ['full_name', 'contact', 'postal_code', 'address', 'city', 'state', 'country', 'total',
                  'service_charges', 'shipping_charges', 'sub_total', 'payment_type', 'order_status', 'payment_status',
                  'stripe_id', 'is_active', 'created_on', 'order_items']  # Change 'order' to 'order_items'


class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ['product', 'rate', 'comment', 'client']

    def validate(self, data):
        user = self.context['request'].user

        client = data['client']
        product = data['product']
        rate = data['rate']
        comment = data['comment']

        if not Product.objects.filter(pk=product.id).exists():
            raise serializers.ValidationError('Product not found')

        if not comment:
            raise serializers.ValidationError('Comment is required')

        if rate < 1 or rate > 5:
            raise serializers.ValidationError('Rating must be between 1 and 5')

        if ProductRating.objects.filter(product=product, client=client).exists():
            raise serializers.ValidationError('Product already rated')
        return data


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'full_name', 'contact', 'postal_code', 'address', 'city', 'state', 'country'
            , 'payment_type',

        ]

    def validate(self, data):
        error = False
        error_message = []
        user = self.context['request'].user
        cart_item = Cart.objects.filter(user=user)
        if not cart_item:
            raise serializers.ValidationError(
                'No items available in cart, to proceed to checkout add some items to cart first.✖')
        for _cart_item in cart_item:
            if _cart_item.quantity >= _cart_item.product.quantity:
                error = True
                error_message.append(f"Insufficient quantity of {_cart_item.product.title} "
                                     f"in stock , Available Quantity is {_cart_item.product.quantity}")
                break
        if error:
            raise serializers.ValidationError(error_message)
        return data
