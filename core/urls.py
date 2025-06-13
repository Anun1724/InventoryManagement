from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sell/<int:product_id>/', views.sell_product, name='sell_product'),
    path('vendors/', views.vendor_order_page, name='vendor_order_page'),
    path('orders/', views.orders_page, name='orders_page'),
    path('create-order/', views.create_order, name='create_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('create-new-product-order/', views.create_new_product_and_order, name='create_new_product_and_order'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),
]