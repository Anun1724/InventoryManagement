# filepath: core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Add more app-specific URLs here
]