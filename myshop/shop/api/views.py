# myshop\shop\api\views.py
from core.api.base import MultilingualViewSet
from ..models import Product
from .serializers import ProductSerializer


class ProductViewSet(MultilingualViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
