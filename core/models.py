from django.db import models

class Vendor(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField()
    min_stock_level = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Order {self.id} - {self.vendor.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of order

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Transaction(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} - {self.total_price}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.amount}"