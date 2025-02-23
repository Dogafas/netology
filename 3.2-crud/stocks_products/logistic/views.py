from rest_framework.viewsets import ModelViewSet
from logistic.models import Product, Stock
from logistic.serializers import ProductSerializer, StockSerializer
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProductViewSet(ModelViewSet):
    """
    API для управления продуктами.

    Этот ViewSet предоставляет CRUD-операции для модели Product:
    - GET /api/products/ - получение списка всех продуктов с возможностью поиска.
    - GET /api/products/{id}/ - получение информации о конкретном продукте.
    - POST /api/products/ - создание нового продукта.
    - PUT /api/products/{id}/ - обновление продукта.
    - DELETE /api/products/{id}/ - удаление продукта.
    """

    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Поиск продуктов по названию или описанию (без учета регистра)",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def get_queryset(self):
        """
        Переопределяет базовый queryset для поддержки поиска.

        Если в запросе передан параметр 'search', фильтрует продукты по названию
        или описанию, игнорируя регистр букв.
        """
        queryset = Product.objects.all().order_by("id")
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(  # Поиск без учета регистра
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return queryset


class StockViewSet(ModelViewSet):
    """
    API для управления складами.

    Этот ViewSet предоставляет CRUD-операции для модели Stock:
    - GET /api/stocks/ - получение списка складов с возможностью фильтрации по продуктам и поиску.
    - GET /api/stocks/{id}/ - получение информации о конкретном складе.
    - POST /api/stocks/ - создание нового склада.
    - PUT /api/stocks/{id}/ - обновление склада.
    - DELETE /api/stocks/{id}/ - удаление склада.
    """

    queryset = Stock.objects.all().order_by("id").prefetch_related("positions__product")
    serializer_class = StockSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "products",
                openapi.IN_QUERY,
                description="Фильтр складов по ID продукта",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Поиск складов по части названия или описания продукта (без учета регистра)",
                type=openapi.TYPE_STRING,
            ),
        ]
    )
    def get_queryset(self):
        """
        Переопределяет базовый queryset для фильтрации складов.

        Поддерживает два фильтра:
        1. 'products' - фильтр по ID продукта, связанного со складом через positions.
        2. 'search' - фильтр по части названия или описания продукта на складе.
        """
        queryset = Stock.objects.all().order_by("id")

        # Фильтрация по ID продукта
        product_id = self.request.query_params.get("products", None)
        if product_id is not None:
            try:
                product_id = int(product_id)
                queryset = queryset.filter(positions__product__id=product_id).distinct()
            except ValueError:
                return (
                    Stock.objects.none()
                )  # Возвращаем пустой набор при некорректном ID

        # Фильтр по части названия или описания продукта
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(
                Q(positions__product__title__icontains=search)
                | Q(positions__product__description__icontains=search)
            ).distinct()

        return queryset
