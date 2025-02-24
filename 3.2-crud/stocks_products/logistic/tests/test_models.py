# stocks_products/logistic/tests/test_models.py
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from logistic.models import Product, Stock, StockProduct


@pytest.mark.django_db
def test_product_creation():
    product = Product.objects.create(
        title="Тестовый товар", description="Тестовое описание для товара"
    )
    assert product.title == "Тестовый товар"
    assert product.description == "Тестовое описание для товара"
    assert str(product) == "Тестовый товар"


@pytest.mark.django_db
def test_product_unique_title():
    Product.objects.create(title="Продукт № 666")
    with pytest.raises(Exception):  # Ожидаем IntegrityError или ValidationError
        Product.objects.create(title="Продукт № 666")


@pytest.mark.django_db
def test_stock_creation():
    stock = Stock.objects.create(address="Тестовый адрес")
    assert stock.address == "Тестовый адрес"
    assert str(stock) == "Тестовый адрес"


@pytest.mark.django_db
def test_stock_unique_address():
    Stock.objects.create(address="адрес новый уникальный")
    with pytest.raises(Exception):
        Stock.objects.create(address="адрес новый уникальный")


@pytest.mark.django_db
def test_stock_product_creation():
    product = Product.objects.create(title="Продукт № 555")
    stock = Stock.objects.create(address="адрес склада №1")
    stock_product = StockProduct.objects.create(
        stock=stock, product=product, quantity=10, price=100.00
    )
    assert stock_product.stock == stock
    assert stock_product.product == product
    assert stock_product.quantity == 10
    assert stock_product.price == 100.00
    assert stock.products.count() == 1
    assert product.positions.count() == 1


@pytest.mark.django_db
def test_stock_product_negative_quantity():
    product = Product.objects.create(title="Тестовый товар")
    stock = Stock.objects.create(address="тестовый адрес склада №2")
    with pytest.raises(IntegrityError):
        StockProduct.objects.create(
            stock=stock, product=product, quantity=-1, price=100.00
        )


@pytest.mark.django_db
def test_stock_product_negative_price():
    product = Product.objects.create(title="Тестовый товар")
    stock = Stock.objects.create(address="тестовый адрес склада №2")
    stock_product = StockProduct(
        stock=stock, product=product, quantity=10, price=-10.00
    )
    with pytest.raises(ValidationError):
        stock_product.full_clean()
