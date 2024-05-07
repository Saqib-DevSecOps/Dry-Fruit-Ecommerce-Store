from django.urls import pathfrom .views import (    DashboardView, UserOwnUpdateView, UserOwnPasswordChangeView,    UserPasswordResetView, UserListView, UserUpdateView, UserDeleteView, UserDetailView, UserCreateView,    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,    BlogCategoryListView, BlogCategoryCreateView, BlogCategoryUpdateView, BlogCategoryDeleteView,    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView,    ProductImageAddView, ProductImageDeleteView,    OrderListView, OrderDetailView, OrderDeleteView, OrderStatusChangeView,    BlogListView, BlogCreateView, BlogUpdateView, BlogDeleteView, BlogDetailView,    WeightListView, WeightCreateView, WeightUpdateView, WeightDeleteView, ProductWeightAddView, ProductWeightDeleteView,    ShipmentUpdateView,)app_name = 'admins'urlpatterns = [    path('', DashboardView.as_view(), name='dashboard'),    path('profile/change/', UserOwnUpdateView.as_view(), name='my-profile-change'),    path('password/change/', UserOwnPasswordChangeView.as_view(), name='my-password-change'),]urlpatterns += [    path('user/', UserListView.as_view(), name='user-list'),    path('user/add/', UserCreateView.as_view(), name='user-add'),    path('user/<str:pk>/', UserDetailView.as_view(), name='user-detail'),    path('user/<str:pk>/change/', UserUpdateView.as_view(), name='user-update'),    path('user/<str:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),    path('user/<str:pk>/reset/password/', UserPasswordResetView.as_view(), name='user-password-reset'),]urlpatterns += [    path('category/', CategoryListView.as_view(), name='category-list'),    path('category/add/', CategoryCreateView.as_view(), name='category-add'),    path('category/<str:pk>/change/', CategoryUpdateView.as_view(), name='category-update'),    path('category/<str:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),    path('post-category/', BlogCategoryListView.as_view(), name='post-category-list'),    path('post-category/add/', BlogCategoryCreateView.as_view(), name='post-category-add'),    path('post-category/<str:pk>/change/', BlogCategoryUpdateView.as_view(), name='post-category-update'),    path('post-category/<str:pk>/delete/', BlogCategoryDeleteView.as_view(), name='post-category-delete'),    path('weight/', WeightListView.as_view(), name='weight-list'),    path('weight/add/', WeightCreateView.as_view(), name='weight-add'),    path('weight/<str:pk>/change/', WeightUpdateView.as_view(), name='weight-update'),    path('weight/<str:pk>/delete/', WeightDeleteView.as_view(), name='weight-delete'),    path('order/', OrderListView.as_view(), name='order-list'),    path('order/<str:pk>/', OrderDetailView.as_view(), name='order-detail'),    path('order/<str:pk>/status/change/', OrderStatusChangeView.as_view(), name='order-status-change'),    path('order/<str:pk>/delete/', OrderDeleteView.as_view(), name='order-delete'),    path('order/<str:pk>/shipment/update/', ShipmentUpdateView.as_view(), name='shipment-update'),    path('post/', BlogListView.as_view(), name='post-list'),    path('post/add/', BlogCreateView.as_view(), name='post-add'),    path('post/<str:pk>/', BlogDetailView.as_view(), name='post-detail'),    path('post/<str:pk>/change/', BlogUpdateView.as_view(), name='post-update'),    path('post/<str:pk>/delete/', BlogDeleteView.as_view(), name='post-delete'),]urlpatterns += [    path('product/', ProductListView.as_view(), name='product-list'),    path('product/add/', ProductCreateView.as_view(), name='product-add'),    path('product/<str:pk>/', ProductDetailView.as_view(), name='product-detail'),    path('product/<str:pk>/change/', ProductUpdateView.as_view(), name='product-update'),    path('product/<str:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),    path('product/<str:product_id>/image/add/', ProductImageAddView.as_view(), name='product-image-add'),    path(        'product/<str:product_id>/image/<str:pk>/delete/',        ProductImageDeleteView.as_view(), name='product-image-delete'    ),    path('product/<str:product_id>/weight/add/', ProductWeightAddView.as_view(), name='product-weight-add'),    path(        'product/<str:product_id>/weight/<str:pk>/delete/',        ProductWeightDeleteView.as_view(), name='product-weight-delete'    ),]