from django.contrib import admin
from .models import Vendor, Product, Order, OrderItem, Transaction, Payment

admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Transaction)
admin.site.register(Payment)