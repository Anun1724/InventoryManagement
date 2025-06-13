from django.shortcuts import render,redirect ,get_object_or_404
from django.db.models import Sum, F, Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from .models import Product, Transaction

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
    # Search functionality
    query = request.GET.get('q', '')
    
    # Filter and category functionality
    filter_type = request.GET.get('filter', 'all')
    category_filter = request.GET.get('category', 'all')
    
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)
    
    # Apply category filter
    if category_filter and category_filter != 'all':
        products = products.filter(category=category_filter)
    
    # Apply other filters
    if filter_type == 'stock':
        products = products.order_by('-stock_quantity')
    elif filter_type == 'price':
        products = products.order_by('price')

    # Get unique categories for dropdown
    categories = Product.objects.values_list('category', flat=True).distinct().order_by('category')

    # Stats
    total_stock = products.aggregate(total=Sum('stock_quantity'))['total'] or 0
    out_of_stock_count = products.filter(stock_quantity=0).count()
    expired_count = products.filter(expiry_date__lt=timezone.now().date()).count()
    total_profit = Transaction.objects.aggregate(total=Sum('total_price'))['total'] or 0

    # Most selling medicines (by total quantity sold)
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