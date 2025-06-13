from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sell/<int:product_id>/', views.sell_product, name='sell_product'),
    path('bulk-sell/', views.bulk_sell_products, name='bulk_sell_products'),  # <-- Add this line
    path('vendors/', views.vendor_order_page, name='vendor_order_page'),
    path('orders/', views.orders_page, name='orders_page'),
    path('create-order/', views.create_order, name='create_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('create-new-product-order/', views.create_new_product_and_order, name='create_new_product_and_order'),
    path('process-bulk-order/', views.process_bulk_order, name='process_bulk_order'),
    path('transactions/', views.transactions_page, name='transactions_page'),
    path('reports/', views.reports_page, name='reports_page'),
]