import pytest
from rest_framework.exceptions import ValidationError
from logistic.models import Product, Stock, StockProduct
from logistic.serializers import ProductSerializer, StockSerializer


@pytest.mark.django_db
def test_product_serializer():
    product = Product.objects.create(
        title="Тестовый продукт", description="Тестовое описание"
    )
    serializer = ProductSerializer(product)
    assert serializer.data == {
        "id": product.id,
        "title": "Тестовый продукт",
        "description": "Тестовое описание",
    }


@pytest.mark.django_db
def test_stock_serializer_create():
    product = Product.objects.create(title="Тестовый продукт")
    data = {
        "address": "Одесса, ул. Мясоедовская д. 4",
        "positions": [{"product": product.id, "quantity": 5, "price": "50.00"}],
    }
    serializer = StockSerializer(data=data)
    assert serializer.is_valid(raise_exception=True)
    stock = serializer.save()
    assert stock.address == "Одесса, ул. Мясоедовская д. 4"
    assert stock.positions.count() == 1
    assert stock.positions.first().quantity == 5
    assert stock.positions.first().price == 50.00


@pytest.mark.django_db
def test_stock_serializer_create_invalid_product():
    data = {
        "address": "Какой-то неправильный адрес",
        "positions": [{"product": 999, "quantity": 5, "price": "50.00"}],
    }
    serializer = StockSerializer(data=data)
    with pytest.raises(ValidationError) as exc:
        serializer.is_valid(raise_exception=True)
    assert 'Invalid pk "999" - object does not exist' in str(exc.value)


@pytest.mark.django_db
def test_stock_serializer_update():
    product = Product.objects.create(title="Тестовый продукт")
    stock = Stock.objects.create(address="Старый адрес")
    StockProduct.objects.create(stock=stock, product=product, quantity=10, price=100)

    data = {
        "address": "Обновленный адрес",
        "positions": [{"product": product.id, "quantity": 20, "price": "200.00"}],
    }
    serializer = StockSerializer(stock, data=data, partial=True)
    assert serializer.is_valid(raise_exception=True)
    updated_stock = serializer.save()
    assert updated_stock.address == "Обновленный адрес"
    assert updated_stock.positions.count() == 1
    assert updated_stock.positions.first().quantity == 20
    assert updated_stock.positions.first().price == 200.00
