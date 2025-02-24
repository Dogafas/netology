import pytest
from rest_framework.test import APIClient
from logistic.models import Product, Stock, StockProduct


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_get_products(client):
    Product.objects.create(
        title="Рыба копченая", description="в упаковке (без маркировки)"
    )
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["title"] == "Рыба копченая"


@pytest.mark.django_db
def test_search_products(client):
    Product.objects.create(title="Сигареты", description="покурка")
    Product.objects.create(
        title="Морковь", description="овощи и фрукты и прочие продукты"
    )
    response = client.get("/api/v1/products/?search=кур")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["title"] == "Сигареты"


@pytest.mark.django_db
def test_get_stocks(client):
    Stock.objects.create(address="Морской проспект 1")
    response = client.get("/api/v1/stocks/")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["address"] == "Морской проспект 1"


@pytest.mark.django_db
def test_filter_stocks_by_product(client):
    product = Product.objects.create(title="тестовый продукт")
    stock = Stock.objects.create(address="тестовый склад")
    StockProduct.objects.create(stock=stock, product=product, quantity=5, price=50)

    response = client.get(f"/api/v1/stocks/?products={product.id}")
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["address"] == "тестовый склад"


@pytest.mark.django_db
def test_create_stock(client):
    product = Product.objects.create(title="тестовый продукт")
    data = {
        "address": "новый склад",
        "positions": [{"product": product.id, "quantity": 5, "price": "50.00"}],
    }
    response = client.post("/api/v1/stocks/", data, format="json")
    assert response.status_code == 201
    assert response.json()["address"] == "новый склад"
    assert len(response.json()["positions"]) == 1


@pytest.mark.django_db
def test_create_stock_invalid_product(client):
    data = {
        "address": "другой склад",
        "positions": [{"product": 999, "quantity": 5, "price": "50.00"}],
    }
    response = client.post("/api/v1/stocks/", data, format="json")
    assert response.status_code == 400
    assert 'Invalid pk "999" - object does not exist' in str(
        response.json()["positions"]
    )


@pytest.mark.django_db
def test_update_stock(client):
    product = Product.objects.create(title="тестовый продукт")
    stock = Stock.objects.create(address="старый склад")
    StockProduct.objects.create(stock=stock, product=product, quantity=10, price=100)

    data = {
        "address": "Новый склад",
        "positions": [{"product": product.id, "quantity": 20, "price": "200.00"}],
    }
    response = client.patch(f"/api/v1/stocks/{stock.id}/", data, format="json")
    assert response.status_code == 200
    assert response.json()["address"] == "Новый склад"
    assert response.json()["positions"][0]["quantity"] == 20


@pytest.mark.django_db
def test_update_stock_with_update_or_create(client):
    product1 = Product.objects.create(title="Рыба копченая")
    product2 = Product.objects.create(title="Цветы (тюльпан)")
    stock = Stock.objects.create(address="старый склад")
    StockProduct.objects.create(stock=stock, product=product1, quantity=10, price=100)

    data = {
        "address": "Новый склад",
        "positions": [
            {"product": product1.id, "quantity": 20, "price": "200.00"},  # Обновление
            {"product": product2.id, "quantity": 5, "price": "50.00"},  # Создание
        ],
    }
    response = client.patch(f"/api/v1/stocks/{stock.id}/", data, format="json")
    assert response.status_code == 200
    assert response.json()["address"] == "Новый склад"
    assert len(response.json()["positions"]) == 2
    assert response.json()["positions"][0]["quantity"] == 20
    assert response.json()["positions"][1]["quantity"] == 5


@pytest.mark.django_db
def test_search_stocks_by_product_name(client):
    # Создаем продукты
    product1 = Product.objects.create(
        title="Помидоры красные", description="Свежие овощи"
    )
    product2 = Product.objects.create(title="Огурцы", description="Зеленые помидоры")
    product3 = Product.objects.create(title="Картофель", description="Клубни")

    # Создаем склады с позициями
    stock1 = Stock.objects.create(address="Склад 1")
    StockProduct.objects.create(stock=stock1, product=product1, quantity=10, price=50)

    stock2 = Stock.objects.create(address="Склад 2")
    StockProduct.objects.create(stock=stock2, product=product2, quantity=5, price=30)

    stock3 = Stock.objects.create(address="Склад 3")
    StockProduct.objects.create(stock=stock3, product=product3, quantity=15, price=20)

    # Поиск по "помид"
    response = client.get("/api/v1/stocks/?search=помид")
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2  # Должны найтись Склад 1 и Склад 2
    assert any(stock["address"] == "Склад 1" for stock in results)
    assert any(stock["address"] == "Склад 2" for stock in results)
    assert not any(stock["address"] == "Склад 3" for stock in results)

    # Поиск по "красные"
    response = client.get("/api/v1/stocks/?search=красные")
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1  # Только Склад 1
    assert results[0]["address"] == "Склад 1"
