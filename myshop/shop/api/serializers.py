# myshop\shop\api\serializers.py
from core.api.base import MultilingualSerializer
from ..models import Product
from parler_rest.fields import TranslatedFieldsField


class ProductSerializer(MultilingualSerializer):
    translations = TranslatedFieldsField(shared_model=Product)

    class Meta(MultilingualSerializer.Meta):
        model = Product
        fields = MultilingualSerializer.Meta.fields + ["price", "category"]
