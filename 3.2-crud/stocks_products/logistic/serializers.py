from rest_framework import serializers

from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = ["id", "title", "description"]


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = ["id", "product", "stock", "quantity"]


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    # настройте сериализатор для склада
    class Meta:
        model = Stock
        fields = ["id", "address", "positions"]

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions_data = validated_data.pop("positions")

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        for position_data in positions_data:
            StockProduct.objects.create(
                stock=stock,
                product=position_data["product"],
                quantity=position_data["quantity"],
                price=position_data["price"],
            )

        return stock

    def update(self, instance, validated_data):
        # Достаем связанные данные для позиций
        positions_data = validated_data.pop("positions")

        # Обновляем основные поля склада
        instance.address = validated_data.get("address", instance.address)
        instance.save()

        # Удаляем старые позиции для этого склада
        instance.positions.all().delete()

        # Создаем новые позиции
        for position_data in positions_data:
            StockProduct.objects.create(
                stock=instance,
                product=position_data["product"],
                quantity=position_data["quantity"],
                price=position_data["price"],
            )

        return instance
