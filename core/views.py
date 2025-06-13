from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.contrib import messages
from .models import Order, OrderItem, Product, Transaction, Vendor

@require_POST
def sell_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    if quantity > 0 and quantity <= product.stock_quantity:
        product.stock_quantity -= quantity
        product.save()
        Transaction.objects.create(
            product=product,
            quantity=quantity,
            total_price=quantity * product.price,
            date=timezone.now()
        )
    return redirect('dashboard')

def dashboard(request):
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')
    category_filter = request.GET.get('category', 'all')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    if category_filter and category_filter != 'all':
        products = products.filter(category=category_filter)
    if filter_type == 'stock':
        products = products.order_by('-stock_quantity')
    elif filter_type == 'price':
        products = products.order_by('price')
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')
    total_stock = products.aggregate(total=Sum('stock_quantity'))['total'] or 0
    out_of_stock_count = products.filter(stock_quantity=0).count()
    expired_count = products.filter(expiry_date__lt=timezone.now().date()).count()
    total_profit = Transaction.objects.aggregate(total=Sum('total_price'))['total'] or 0
    most_selling = (
        Product.objects.annotate(units_sold=Sum('transaction__quantity'))
        .order_by('-units_sold')
        .filter(units_sold__isnull=False)[:5]
    )
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_filter,
        'selected_filter': filter_type,
        'total_stock': total_stock,
        'out_of_stock_count': out_of_stock_count,
        'expired_count': expired_count,
        'total_profit': total_profit,
        'most_selling': most_selling,
        'query': query,
    }
    return render(request, 'core/dashboard.html', context)

def vendor_order_page(request):
    # Exclude products that are already in a pending order
    pending_product_ids = OrderItem.objects.filter(order__status='pending').values_list('product_id', flat=True)
    products = Product.objects.filter(
        Q(stock_quantity__lte=F('min_stock_level')) | Q(expiry_date__lt=timezone.now().date())
    ).exclude(id__in=pending_product_ids).distinct()
    vendors = Vendor.objects.all()
    categories = Product.objects.values_list('category', flat=True).distinct()
    today = timezone.now().date()
    context = {
        'products': products,
        'vendors': vendors,
        'categories': categories,
        'today': today,
    }
    return render(request, 'core/vendor_order.html', context)

def orders_page(request):
    orders = Order.objects.all().order_by('-date')
    context = {
        'orders': orders,
    }
    return render(request, 'core/orders.html', context)

@require_POST
def create_order(request):
    vendor_id = request.POST.get('vendor')
    product_id = request.POST.get('product')
    quantity = request.POST.get('quantity')
    unit_price = request.POST.get('unit_price')
    if all([vendor_id, product_id, quantity, unit_price]):
        vendor = get_object_or_404(Vendor, id=vendor_id)
        product = get_object_or_404(Product, id=product_id)
        order = Order.objects.create(vendor=vendor)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=unit_price
        )
        # Do NOT increase stock here!
        return redirect('vendor_order_page')
    return redirect('vendor_order_page')

@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled'
    order.save()
    return redirect('orders_page')

@require_POST
def complete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status == 'pending':
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            item.product.save()
        order.status = 'completed'
        order.save()
    return redirect('orders_page')

@require_POST
def create_new_product_and_order(request):
    name = request.POST.get('name')
    category = request.POST.get('category')
    new_category = request.POST.get('new_category')
    price = request.POST.get('price')
    vendor_id = request.POST.get('vendor')
    new_vendor = request.POST.get('new_vendor')
    new_vendor_contact = request.POST.get('new_vendor_contact')
    quantity = request.POST.get('quantity')
    expiry_date = request.POST.get('expiry_date')

    if new_category:
        category = new_category

    if new_vendor:
        vendor, created = Vendor.objects.get_or_create(name=new_vendor, defaults={'contact_info': new_vendor_contact})
    else:
        vendor = get_object_or_404(Vendor, id=vendor_id)

    if all([name, category, price, vendor, quantity, expiry_date]):
        # Set stock_quantity to 0 so it appears in vendor list until order is completed
        product = Product.objects.create(
            name=name,
            category=category,
            price=price,
            stock_quantity=0,
            min_stock_level=0,
            expiry_date=expiry_date,
            vendor=vendor
        )
        order = Order.objects.create(vendor=vendor)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price
        )
        messages.success(request, "Product added and order placed!")
        return redirect('vendor_order_page')
    messages.error(request, "Please fill all fields.")
    return redirect('vendor_order_page')