# filepath: core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('sell/<int:product_id>/', views.sell_product, name='sell_product'),
    # Add more app-specific URLs here
]