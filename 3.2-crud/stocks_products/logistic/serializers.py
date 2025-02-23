from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "description"]
        extra_kwargs = {
            "id": {"help_text": "ID продукта "},
            "title": {"help_text": "Название продукта (обязательное поле)"},
            "description": {"help_text": "Описание продукта (может быть пустым)"},
        }


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ["product", "quantity", "price"]
        extra_kwargs = {
            "product": {"help_text": "Ссылка на продукт (ID существующего продукта)"},
            "quantity": {
                "help_text": "Количество продукта (обязательное поле, больше 0)"
            },
            "price": {
                "help_text": "Цена продукта на складе (обязательное поле, с двумя знаками после зпт.)"
            },
        }


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(
        many=True, help_text="Список позиций продуктов на складе"
    )

    class Meta:
        model = Stock
        fields = ["id", "address", "positions"]
        extra_kwargs = {
            "id": {"help_text": "Уникальный идентификатор склада"},
            "address": {"help_text": "Адрес склада (обязательное поле)"},
        }

    def create(self, validated_data):
        # Извлекаем данные позиций
        positions_data = validated_data.pop("positions", [])
        # Создаем склад
        stock = Stock.objects.create(**validated_data)
        try:
            # Создаем позиции
            for position_data in positions_data:
                product = position_data["product"]
                if not Product.objects.filter(id=product.id).exists():
                    raise serializers.ValidationError(
                        {"positions": f"Product with id {product.id} does not exist."}
                    )
                StockProduct.objects.create(stock=stock, **position_data)
        except Exception as e:
            stock.delete()  # Удаляем склад при ошибке
            raise serializers.ValidationError({"positions": str(e)})
        return stock

    def update(self, instance, validated_data):
        positions_data = validated_data.pop("positions", [])
        instance.address = validated_data.get("address", instance.address)
        instance.save()

        # Обновляем или создаем позиции
        for position_data in positions_data:
            product = position_data.get("product")
            if not Product.objects.filter(id=product.id).exists():
                raise serializers.ValidationError(
                    {"positions": f"Product with id {product.id} does not exist."}
                )
            StockProduct.objects.update_or_create(
                stock=instance,
                product=product,
                defaults={
                    "quantity": position_data.get("quantity"),
                    "price": position_data.get("price"),
                },
            )

        # Удаляем позиции, которых нет в новом списке
        new_product_ids = {position["product"].id for position in positions_data}
        instance.positions.exclude(product__id__in=new_product_ids).delete()

        return instance
