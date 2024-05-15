from django.db.models import Sum, Subquery, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.generics import (
    CreateAPIView, ListAPIView, get_object_or_404,
    ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, DestroyAPIView, GenericAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response

from src.administration.admins.bll import get_cart_calculations
from src.administration.admins.filters import OrderFilter
from src.administration.admins.models import ProductCategory, Product, Cart, Order, Wishlist, OrderItem, Payment, \
    ProductRating, Shipment
from src.api.filter import ProductFilter
from src.api.serializer import OrderCreateSerializer, ProductSerializer, \
    ProductDetailSerializer, HomeProductsListSerializer, CartListSerializer, CartCreateSerializer, CartUpdateSerializer, \
    WishlistListSerializer, WishlistCreateSerializer, WishlistDeleteSerializer, OrderSerializer, \
    ProductRatingSerializer, OrderDetailSerializer, PaymentSuccessSerializer, ProductRatingListSerializer, \
    OrderItemListSerializer, ShipmentSerializer
from src.apps.razorpay.bll import get_razorpay_order_id
from src.apps.shipment.bll import track_shipping

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
        new_products = Product.objects.all().order_by('-created_on')[:5]
        most_sales = Product.objects.order_by('-quantity')[:5]
        top_discounted_products = Product.objects.order_by('-discount')[:5]
        categories = ProductCategory.objects.all()[:12]

        return {
            'new_products': new_products,
            'top_discounted_products': top_discounted_products,
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


class ProductPendingRatingListView(ListAPIView):
    serializer_class = OrderItemListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return OrderItem.objects.none()
        # Subquery to get the products in the order that the user has already rated
        rated_products_subquery = ProductRating.objects.filter(
            client=self.request.user,
            product_id=OuterRef('product_id'),
            order_id=OuterRef('order_id')
        ).values('product_id')

        # Query to get order items where the product in the order has not been rated by the user
        order_items_without_review = OrderItem.objects.filter(
            order__client=self.request.user
        ).exclude(
            product_id__in=Subquery(rated_products_subquery)
        )

        return order_items_without_review


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
        razorpay_order_id = None
        user = self.request.user
        total, service_charges, shipping_charges, sub_total = get_cart_calculations(user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(client=user, total=total, service_charges=service_charges)
        if order.is_online():
            razorpay_order_id = get_razorpay_order_id(self, request, order.id)
        return Response({'data': serializer.data, 'razorpay_order_id': razorpay_order_id},
                        status=status.HTTP_201_CREATED)


class PaymentSuccessAPIView(GenericAPIView):
    serializer_class = PaymentSuccessSerializer

    def post(self, request):
        serializer = PaymentSuccessSerializer(data=request.data)
        if serializer.is_valid():
            razorpay_order_id = serializer.validated_data.get('razorpay_order_id')
            razorpay_payment_id = serializer.validated_data.get('razorpay_payment_id')
            razorpay_signature = serializer.validated_data.get('razorpay_signature')
            # Add your validation logic here
            try:
                order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
                order.payment_status = 'paid'
                order.order_status = 'approved'

                order_items = OrderItem.objects.filter(order=order)
                for order_item in order_items:
                    if order_item.product.quantity >= order_item.qty:
                        product = order_item.product
                        ordered_quantity = order_item.qty
                        product.quantity -= ordered_quantity
                        product.save()
                order.save()
                payment = get_object_or_404(Payment, order=order)
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_order_id = razorpay_order_id
                payment.razorpay_signature_id = razorpay_signature
                payment.payment_status = "completed"
                payment.amount_paid = order.sub_total
                payment.save()
                return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
            except:
                return Response({'message': 'Payment processing failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentRetrieveAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShipmentSerializer
    queryset = Shipment.objects.all()


class ShipRocketShipmentRetrieveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            shipment_detail, status_code = track_shipping(pk)
            if not status.is_success(status_code):
                return Response({'error': 'Error occurred while fetching shipment details'},
                                status=status.HTTP_400_BAD_REQUEST)
            shipment_data = shipment_detail.json()
            first_key = list(shipment_data.keys())[0]
            tracking_data = shipment_data[first_key].get('tracking_data')
            return Response(tracking_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)