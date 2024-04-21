from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, serializers
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.administration.admins.models import OrderItem, Order, Cart, Product, Wishlist, Blog
from src.api.filter import ProductFilter, BlogFilter
from src.api.serializer import OrderItemSerializer, OrderSerializer, ProductSerializer, CartSerializer, \
    WishlistSerializer, BlogSerializer


class ProductListAPIView(generics.ListAPIView):
    """
    Product List API:


    # Endpoint :
        /api/products/
    # Method :
    GET
    # Description :
    Fetches a list of products.
    # Query Parameters:
        category: Filter products by category.
        search: Search products by name or category.
    # Response:
     Returns a list of products with details.

    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = ['name', 'category']


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    Product Detail API:


    # Endpoint:
        /api/products/{id}/
    # Method:
    GET
    # Description:
    Fetches details of a specific product.
    # Path Parameters:
            id: The ID of the product.
    # Response:
    Returns the details of the product.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'

    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        # Increment click count
        instance.clicks += 1
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CartItemListAPIView(generics.ListAPIView):
    """
     Cart Item List API:

    # Endpoint:
        /api/cart/
    # Method:
    GET
    # Description:
    Fetches a list of cart items for the authenticated user.
    # Authorization:
    Requires authentication.
    # Response:
    Returns a list of cart items.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)


class CartItemAPIView(generics.CreateAPIView):
    """
    Add Cart Item API

    # Endpoint:
        /api/cart/add/
    # Method:
    POST
    # Description:
    Adds a new item to the user's cart.
    # Authorization:
    Requires authentication.
    # Request Body:
        Requires product_id (ID of the product) and quantity (optional, default: 1).
    # Response:
    Returns the added cart item.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get('product')
        quantity = self.request.data.get('quantity', 1)
        if not quantity:
            quantity = 1
        if not product_id:
            raise ValidationError("Product ID is required.")

        cart, created = Cart.objects.get_or_create(user=self.request.user, product_id=product_id)
        cart.quantity = quantity
        cart.save()
        serializer.instance = cart

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class IncrementCartItemAPIView(generics.UpdateAPIView):
    """
    Increment Cart Item API

    # Endpoint:
        /api/cart/increment/{increment_cart_item_id}/
    # Method:
    PUT
    # Description:
     Increments the quantity of a specific cart item.
    # Authorization:
     Requires authentication.
    # Path Parameters:
        increment_cart_item_id: The ID of the cart item to increment.
    # Response:
    Returns the updated cart item.

    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    lookup_url_kwarg = 'increment_cart_item_id'
    http_method_names = ['put']

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_update(self, serializer):
        try:
            cart = self.get_object()
            cart.quantity += 1
            cart.save()
            serializer.instance = cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart item not found.")


class DecrementCartItemAPIView(generics.UpdateAPIView):
    """
    Decrement Cart Item AP

    # Endpoint:
        /api/cart/decrement/{decrement_cart_item_id}/
    # Method:
     PUT
    # Description:
     Decrements the quantity of a specific cart item.
    # Authorization:
     Requires authentication.
    # Path Parameters:
        decrement_cart_item_id: The ID of the cart item to decrement.
    # Response:
     Returns the updated cart item.

    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    lookup_url_kwarg = 'decrement_cart_item_id'
    http_method_names = ['put']

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_update(self, serializer):
        try:
            cart = self.get_object()
            if cart.quantity > 1:
                cart.quantity -= 1
                cart.save()
                serializer.instance = cart
        except Cart.DoesNotExist:
            raise serializers.ValidationError("Cart item not found.")


class DeleteCartItemAPIView(generics.DestroyAPIView):
    """
    Delete Cart Item API

    # Endpoint:
        /api/cart/delete/{delete_cart_item_id}/
    # Method:
     DELETE
    # Description:
     Deletes a specific cart item.
    # Authorization:
     Requires authentication.
    # Path Parameters:
        delete_cart_item_id: The ID of the cart item to delete.
    # Response:
     Returns a success message.

    """
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'delete_cart_item_id'
    http_method_names = ['delete']

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)

    def perform_destroy(self, instance):
        instance.delete()
        return Response({'message': 'Cart item deleted successfully.'})


class WishlistListAPIView(generics.ListAPIView):
    """
    Wishlist API

    # Endpoint:
        /api/wishlist/
    # Method:
     GET
    # Description:
     Fetches a list of wishlist items for the authenticated user.
    # Authorization:
     Requires authentication.
    # Response:
     Returns a list of wishlist items.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(user=user)


class WishlistCreateAPIView(generics.CreateAPIView):
    """
    Add Wishlist Item API

    # Endpoint:
        /api/wishlist/add/
    # Method:
     POST
    # Description:
     Adds a new item to the user's wishlist.
    # Authorization:
     Requires authentication.
    # Request Body:
        Requires product_id (ID of the product).
    # Response:
     Returns the added wishlist item.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer

    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.request.data.get('product')
        print(product_id)

        # Check if the product is already in the wishlist for the user
        if Wishlist.objects.filter(user=user, product_id=product_id):
            raise ValidationError("Product already exists in the wishlist.")

        serializer.save(user=user)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class WishlistDeleteAPIView(generics.DestroyAPIView):
    """
    Delete Wishlist Item API

    # Endpoint:
        /api/wishlist/delete/{wishlist_item_id}/
    # Method:
     DELETE
    # Description:
     Deletes a specific wishlist item.
    # Authorization:
     Requires authentication.
    # Path Parameters:
        wishlist_item_id: The ID of the wishlist item to delete.
    # Response:
     Returns a success message.
    """
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'wishlist_item_id'
    http_method_names = ['delete']

    def get_queryset(self):
        user = self.request.user
        return Wishlist.objects.filter(user=user)

    def perform_destroy(self, instance):
        instance.delete()
        return Response({'message': 'Product removed from the wishlist.'})


class PostListAPIView(generics.ListAPIView):
    """
    Post List API

    # Endpoint:
        /api/posts/
    # Method:
     GET
    # Description:
        Fetches a list of blog posts.
    # Query Parameters:
        category: Filter posts by category.
        search: Search posts by title or category.
    # Response:
     Returns a list of blog posts.

    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = BlogFilter
    search_fields = ['title', 'category__name']


class PostDetailAPIView(generics.RetrieveAPIView):
    """
    Post Detail API

    # Endpoint:
        /api/posts/{slug}/
    # Method:
     GET
    # Description:
     Fetches details of a specific blog post.
    # Path Parameters:
        slug: The slug of the blog post.
    # Response:
     Returns the details of the post.
    """
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    lookup_field = 'slug'


# Create your views here.
class PurchasedItemListAPIView(generics.ListAPIView):
    """
    Purchased Item List API View.

    # Description:
    This API view returns a list of purchased items for the authenticated user.

    # Endpoint:
        /api/purchased-items/
    # HTTP Methods:
     GET
    # Permission:
     IsAuthenticated

    # Response:
        - 200 OK: Returns the list of purchased items for the user.
        - 401 Unauthorized: If the user is not authenticated.

    # Used Serializers:
        - OrderItemSerializer

    """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderItemSerializer

    def get_queryset(self):
        user = self.request.user
        order_items = OrderItem.objects.filter(order__user=user)
        return order_items


class OrderCreateAPIView(generics.CreateAPIView):
    """
       Order Create API View.

       # Description:
       This API view allows authenticated users to create an order by providing the necessary details and transferring
       the items from their cart to the order.

       # Endpoint:
            /api/orders/
       # HTTP Methods:
        POST
       # Permission:
        IsAuthenticated

       # Request Body:
            - name: String field for the billing name.
            - street_address: String field for the street address.
            - postal_code: String field for the postal code.
            - city: String field for the city.
            - country: String field for the country.
            - phone: String field for the phone number.
            - email: String field for the email address.

       # Response:
            - 201 Created: Returns the created order details.
            - 400 Bad Request: If the request data is invalid.
            - 401 Unauthorized: If the user is not authenticated.

       # Used Serializers:
            - OrderSerializer

       """
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
    """
       Order Detail API View.

       # Description:
       This API view returns the details of a specific order for the authenticated user.

       # Endpoint:
            /api/orders/<order_id>/
       # HTTP Methods:
        GET
       # Permission:
        IsAuthenticated

       # Response:
            - 200 OK: Returns the details of the specified order.
            - 401 Unauthorized: If the user is not authenticated.
            - 404 Not Found: If the specified order does not exist or does not belong to the user.

       # Used Serializers:
            - OrderSerializer

       """
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)
