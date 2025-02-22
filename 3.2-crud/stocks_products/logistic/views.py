from rest_framework.viewsets import ModelViewSet
from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer
from django.db.models import Q


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(  # поиск продуктов без учета регистра
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return queryset


class StockViewSet(ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer

    # при необходимости добавьте параметры фильтрации
    def get_queryset(self):
        queryset = Stock.objects.all()
        product_id = self.request.query_params.get("products", None)
        if product_id is not None:
            queryset = queryset.filter(positions__products__id=product_id).distinct
        return queryset
