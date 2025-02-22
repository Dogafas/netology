from rest_framework import serializers
from .models import Product, Stock, StockProduct


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "description"]


class ProductPositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockProduct
        fields = ["product", "quantity", "price"]


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    class Meta:
        model = Stock
        fields = ["id", "address", "positions"]

    def create(self, validated_data):
        positions_data = validated_data.pop("positions")
        stock = Stock.objects.create(**validated_data)
        try:
            for position_data in positions_data:
                product_id = position_data["product"].id
                # Проверяем, существует ли продукт
                if not Product.objects.filter(id=product_id).exists():
                    raise serializers.ValidationError(
                        {"positions": f"Product with id {product_id} does not exist."}
                    )
                StockProduct.objects.create(stock=stock, **position_data)
        except Exception as e:
            # Удаляем склад, если произошла ошибка, чтобы не оставлять "мусор"
            stock.delete()
            raise serializers.ValidationError({"positions": str(e)})
        return stock

    def update(self, instance, validated_data):
        positions_data = validated_data.pop("positions")
        instance.address = validated_data.get("address", instance.address)
        instance.save()
        try:
            instance.positions.all().delete()
            for position_data in positions_data:
                product_id = position_data["product"].id
                # Проверяем, существует ли продукт
                if not Product.objects.filter(id=product_id).exists():
                    raise serializers.ValidationError(
                        {"positions": f"Product with id {product_id} does not exist."}
                    )
                StockProduct.objects.create(stock=instance, **position_data)
        except Exception as e:
            raise serializers.ValidationError({"positions": str(e)})
        return instance
