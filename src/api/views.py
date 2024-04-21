from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.administration.admins.models import OrderItem, Order, Cart, Product, Wishlist, Blog, ProductCategory
from src.api.filter import ProductFilter, BlogFilter
from src.api.serializer import OrderItemSerializer, OrderSerializer, ProductCategorySerializer, ProductListSerializer, \
    ProductDetailSerializer, CartListSerializer, CartUpdateSerializer, WishlistSerializer, CartAddSerializer


class HomeAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            product_categories = ProductCategory.objects.filter(is_active=True)
            products_new = Product.objects.filter(is_active=True)[0:10]
            products_feature = Product.objects.filter(is_active=True)[0:6]
            products_top_order = Product.objects.filter(is_active=True).order_by(
                '-created_on')[0:10]
            products_top_rated = Product.objects.filter(is_active=True).order_by(
                '-average_review')[
                                 0:10]
            products_top_discount = Product.objects.filter(is_active=True).order_by('-discount')[0:10]

            # Serialize data
            product_category_serializer = ProductCategorySerializer(product_categories, many=True)
            product_serializer = ProductListSerializer(products_new, many=True)
            products_feature_serializer = ProductListSerializer(products_feature, many=True)
            products_top_order_serializer = ProductListSerializer(products_top_order, many=True)
            products_top_rated_serializer = ProductListSerializer(products_top_rated, many=True)
            products_top_discount_serializer = ProductListSerializer(products_top_discount, many=True)

            # Return response
            return Response({
                'product_categories': product_category_serializer.data,
                'products_new': product_serializer.data,
                'products_feature': products_feature_serializer.data,
                'products_top_order': products_top_order_serializer.data,
                'products_top_rated': products_top_rated_serializer.data,
                'products_top_discount': products_top_discount_serializer.data,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'error': f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ['name', 'category']


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class CartItemListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartListSerializer
    queryset = Cart.objects.all()


    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)


class CartItemAddAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartAddSerializer

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get('product')
        product_weight = self.request.data.get('product_weight')
        if Cart.objects.filter(user=user, product_id=product_id, product_weight_id=product_weight):
            raise ValidationError("Product already exists in the Cart.")
        serializer.save(user=user)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class CartItemUpdateAPIView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartUpdateSerializer

    def get_queryset(self):
        return Cart.objects.filter(id=self.kwargs.get('id'), user=self.request.user)


class DeleteCartItemAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(id=self.kwargs.get('id'), user=self.request.user)

    def perform_destroy(self, instance):
        instance.delete()
        return Response({'message': 'Cart item deleted successfully.'})


class WishlistListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(user=user)


class WishlistCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get('product')
        if Wishlist.objects.filter(user=user, product_id=product_id):
            raise ValidationError("Product already exists in the wishlist.")
        serializer.save(user=user)

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class WishlistDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'wishlist_item_id'
    http_method_names = ['delete']

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(user=user)

    def perform_destroy(self, instance):
        instance.delete()
        return Response({'message': 'Product removed from the wishlist.'})


# Create your views here.
class PurchasedItemListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        order_items = OrderItem.objects.filter(order__user=user)
        return order_items


class OrderCreateAPIView(generics.CreateAPIView):
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
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)
