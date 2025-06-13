from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
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
    # Only count products that are out of stock and not expired
    out_of_stock_count = products.filter(stock_quantity=0, expiry_date__gte=timezone.now().date()).count()
    # Only count products that are expired (regardless of stock)
    expired_count = products.filter(expiry_date__lt=timezone.now().date()).count()
    total_profit = Transaction.objects.aggregate(total=Sum('total_price'))['total'] or 0
    most_selling = (
        Product.objects.annotate(units_sold=Sum('transaction__quantity'))
        .order_by('-units_sold')
        .filter(units_sold__isnull=False)[:5]
    )
    today = timezone.now().date()
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
        'today': today,
    }
    return render(request, 'core/dashboard.html', context)

def vendor_order_page(request):
    # Show products that are out of stock, low stock, or expired
    products = Product.objects.filter(
        Q(stock_quantity__lte=F('min_stock_level')) | Q(expiry_date__lt=timezone.now().date())
    ).distinct()
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
    today = timezone.now().date()
    if order.status == 'pending':
        for item in order.items.all():
            item.product.stock_quantity += item.quantity
            if item.product.expiry_date < today:
                new_expiry = today.replace(year=today.year + 2)
                try:
                    item.product.expiry_date = new_expiry
                except ValueError:
                    item.product.expiry_date = new_expiry.replace(day=28)
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

@require_POST
def bulk_sell_products(request):
    product_ids = request.POST.getlist('product_id')
    quantities = request.POST.getlist('quantity')
    errors = []
    for pid, qty in zip(product_ids, quantities):
        try:
            product = Product.objects.get(id=pid)
            qty = int(qty)
            if qty > 0 and qty <= product.stock_quantity:
                product.stock_quantity -= qty
                product.save()
                Transaction.objects.create(
                    product=product,
                    quantity=qty,
                    total_price=qty * product.price,
                    date=timezone.now()
                )
            else:
                errors.append(f"{product.name}: Invalid quantity")
        except Exception as e:
            errors.append(str(e))
    if errors:
        messages.error(request, "Some products could not be sold: " + "; ".join(errors))
    else:
        messages.success(request, "Products sold successfully!")
    return redirect('dashboard')

@csrf_exempt
@require_POST
def process_bulk_order(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        if not items:
            return JsonResponse({'success': False, 'message': 'No items in cart'})
        total_amount = 0
        total_items = 0
        with transaction.atomic():
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    return JsonResponse({'success': False, 'message': f'Product not found'})
                if product.stock_quantity < quantity:
                    return JsonResponse({
                        'success': False, 
                        'message': f'Insufficient stock for {product.name}. Available: {product.stock_quantity}'
                    })
                if product.expiry_date < timezone.now().date():
                    return JsonResponse({
                        'success': False, 
                        'message': f'{product.name} has expired'
                    })
                item_total = product.price * quantity
                total_amount += item_total
                total_items += quantity
                product.stock_quantity -= quantity
                product.save()
                Transaction.objects.create(
                    product=product,
                    quantity=quantity,
                    total_price=item_total,
                    date=timezone.now()
                )
        return JsonResponse({
            'success': True,
            'message': f'Order processed successfully',
            'total_amount': total_amount,
            'total_items': total_items
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    
def transactions_page(request):
    transactions = Transaction.objects.select_related('product').order_by('-date')
    context = {
        'transactions': transactions,
    }
    return render(request, 'core/transactions.html', context)

def reports_page(request):
    most_selling = (
        Product.objects.annotate(units_sold=Sum('transaction__quantity'))
        .order_by('-units_sold')
        .filter(units_sold__isnull=False)[:10]
    )
    context = {
        'most_selling': most_selling,
    }
    return render(request, 'core/reports.html', context)