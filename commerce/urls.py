from django.urls import path
from . import views

urlpatterns = [
    # Product Category URLs
    path('product-categories/', views.ProductCategoryList.as_view(), name='product-category-list'),
    path('product-categories/<int:pk>/', views.ProductCategoryDetail.as_view(), name='product-category-detail'),

    # Store URLs
    path('stores/', views.StoreList.as_view(), name='store-list'),
    path('stores/<int:pk>/', views.StoreDetail.as_view(), name='store-detail'),

    # Product URLs
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),

    # Product Review
    path('reviews/', views.ProductReviewListCreateView.as_view(), name='product-review-list'),
    path('reviews/<int:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),

    # CartItem URLs
    path('cart-items/', views.CartItemList.as_view(), name='cart-item-list'),
    path('cart-items/<int:pk>/', views.CartItemDetail.as_view(), name='cart-item-detail'),

    # Order URLs
    path('orders/', views.OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),
]
