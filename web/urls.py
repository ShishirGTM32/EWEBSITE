from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('shop/', views.shop_view, name='shop'),
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:watch_id>/', views.add_to_cart, name='add_to_cart'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('thank-you/', views.thank_you_view, name='contact_thank_you'),
    path('login-register/', views.login_register_view, name='login_register'),
    path('logout/', views.logout_view, name='logout'),
    path('account/', views.account_view, name='account'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_success/<int:order_id>/', views.order_success_view, name='order_success_view'),
]
