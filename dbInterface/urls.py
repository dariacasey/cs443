from django.urls import path
from .views import ProductDetail, AllProducts
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('products/', AllProducts.as_view(), name='products'),
    path('product/<int:pk>/', ProductDetail.as_view(), name='product_detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('login/', views.login_user, name='login_user'),
    path('logout_user/', views.logout_user, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('search/', views.search_results_view, name='search_results')
]