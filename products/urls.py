from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Home & Auth
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Orders
    path('dashboard/', views.dashboard, name='dashboard'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    path('cancel-order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    
    # Products
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    
    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # Checkout & Payment
    path('checkout/', views.checkout, name='checkout'),
    path('payment/', views.payment, name='payment'),
    path('processing/', views.processing, name='processing'),
    path('success/', views.success, name='success'),
    
    # Contact
    path('contact/', views.contact, name='contact'),
    path('send-contact/', views.send_contact, name='send_contact'),
]