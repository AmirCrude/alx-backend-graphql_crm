import django_filters
from .models import Customer, Product, Order
import django_filters

class CustomerFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    created_at_gte = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_lte = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    # Custom filter for phone pattern (starts with +1)
    phone_pattern = django_filters.CharFilter(method='filter_phone_starts_with')
    
    class Meta:
        model = Customer
        fields = ['name', 'email', 'created_at']
    
    def filter_phone_starts_with(self, queryset, name, value):
        """Filter customers whose phone starts with specific pattern"""
        return queryset.filter(phone__startswith=value)

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    stock_gte = django_filters.NumberFilter(field_name='stock', lookup_expr='gte')
    stock_lte = django_filters.NumberFilter(field_name='stock', lookup_expr='lte')
    
    # Custom filter for low stock
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']
    
    def filter_low_stock(self, queryset, name, value):
        """Filter products with stock less than 10"""
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='gte')
    total_amount_lte = django_filters.NumberFilter(field_name='total_amount', lookup_expr='lte')
    order_date_gte = django_filters.DateFilter(field_name='order_date', lookup_expr='gte')
    order_date_lte = django_filters.DateFilter(field_name='order_date', lookup_expr='lte')
    
    # Filter by customer name (related field)
    customer_name = django_filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    
    # Filter by product name (related field through ManyToMany)
    product_name = django_filters.CharFilter(field_name='products__name', lookup_expr='icontains')
    
    # Filter by specific product ID
    product_id = django_filters.NumberFilter(field_name='products__id')
    
    class Meta:
        model = Order
        fields = ['total_amount', 'order_date']