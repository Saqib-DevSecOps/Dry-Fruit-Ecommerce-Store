from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import (
    CreateAPIView, ListAPIView, get_object_or_404,
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from src.administration.admins.bll import get_cart_calculations
from src.administration.admins.filters import OrderFilter
from src.administration.admins.models import ProductCategory, Product, Cart, Order, Wishlist
from src.api.filter import ProductFilter
from src.api.serializer import OrderCreateSerializer, ProductSerializer, \
    ProductDetailSerializer, HomeProductsListSerializer, CartListSerializer, CartCreateSerializer, CartUpdateSerializer, \
    WishlistListSerializer, WishlistCreateSerializer, WishlistDeleteSerializer, OrderSerializer, \
    ProductRatingSerializer, OrderDetailSerializer

from src.apps.stripe.views import create_stripe_checkout_session


"""Product Apis"""


class ProductListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    queryset = Product.objects.all()


""" HOME """


class HomeProductsListAPIView(ListAPIView):
    serializer_class = HomeProductsListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        all_products = Product.objects.all()[:5]
        new_products = Product.objects.all().order_by('-created_on')[:5]
        most_sales = Product.objects.order_by('-quantity')[:5]
        categories = ProductCategory.objects.all()[:12]

        return {
            'all_products': all_products,
            'new_products': new_products,
            'most_sales': most_sales,
            'categories': categories,
        }

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        return Response(serializer.data)


"""Cart Apis"""


class CartListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartListSerializer
        return CartCreateSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CartListSerializer
        return CartUpdateSerializer

    def get_object(self):
        return get_object_or_404(Cart, id=self.kwargs['pk'], user=self.request.user)


"""Wishlist Apis"""


class WishlistListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return WishlistListSerializer
        return WishlistCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


class WishlistDeleteAPIView(DestroyAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistDeleteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        return get_object_or_404(Wishlist, user=user, id=self.kwargs['pk'])


"""Buyer Apis"""


@permission_classes([IsAuthenticated])
class BuyerDashboardAPIView(APIView):
    def get(self, request, *args, **kwargs):
        sum_of_sub_total = Order.objects.filter(client=self.request.user, order_status='completed') \
                               .aggregate(Sum('sub_total'))['sub_total__sum'] or 0
        order_purchases = sum_of_sub_total
        orders_total = Order.objects.filter(client=self.request.user).count()
        orders_active = Order.objects.filter(client=self.request.user,
                                             order_status__in=['pending', 'approved', 'delivery']).count()
        response_data = {
            'order_purchases': order_purchases,
            'orders_total': orders_total,
            'orders_active': orders_active,
        }

        return Response(response_data)


class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_queryset(self):
        return Order.objects.filter(client=self.request.user)


class OrderDetailAPIView(ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Order.objects.none()

        order_id = self.kwargs.get('pk')
        return Order.objects.filter(client=self.request.user, id=order_id)


class ProductRatingAddAPIView(CreateAPIView):
    serializer_class = ProductRatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


"""Order Apis"""


class OrderCreateApiView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer
    queryset = Order.objects.all()

    def create(self, request, *args, **kwargs):
        session_url = None
        user = self.request.user
        total, service_charges, shipping_charges, sub_total = get_cart_calculations(user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(client=user, total=total, service_charges=service_charges)
        if order.is_online():
            session_url = create_stripe_checkout_session(self.request, order)
        return Response({'session_url': session_url, 'data': serializer.data}, status=status.HTTP_201_CREATED)