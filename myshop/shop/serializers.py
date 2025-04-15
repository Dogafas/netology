# myshop\shop\serializers.py
from rest_framework import serializers
from .models import Product, ProductImage, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["image"]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category = CategorySerializer(
        read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "price",
            "available",
            "created",
            "updated",
            "images",
        ]
