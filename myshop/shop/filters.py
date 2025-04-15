# myshop\shop\filters.py
# shop/filters.py
from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError
from .models import Product, Category


class ProductFilter(filters.FilterSet):
    category = filters.NumberFilter(method="filter_category")

    def filter_category(self, queryset, name, value):
        if not Category.objects.filter(id=value).exists():
            raise ValidationError(
                {"category": f"Категория с id={value} не найдена."}, code="invalid"
            )
        return queryset.filter(category_id=value)

    class Meta:
        model = Product
        fields = ["category", "available", "price"]
