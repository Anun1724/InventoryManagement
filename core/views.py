from django.shortcuts import render
from django.db.models import Sum, F, Q
from django.utils import timezone
from .models import Product, Transaction

def dashboard(request):
    # Search functionality
    query = request.GET.get('q', '')
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)

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
        'total_stock': total_stock,
        'out_of_stock_count': out_of_stock_count,
        'expired_count': expired_count,
        'total_profit': total_profit,
        'most_selling': most_selling,
        'query': query,
    }
    return render(request, 'core/dashboard.html', context)