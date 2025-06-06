# myshop\shop\tests\test_models.py
from django.test import TestCase
from parler.utils.context import switch_language
from shop.models import Product, Category


class ParlerCacheTest(TestCase):
    def setUp(self):
        # Создаем тестовую категорию один раз для всех тестов
        self.category = Category.objects.create(name="Test Category")

    def test_cache_behavior(self):
        product = Product.objects.create(price=100, category=self.category)

        with switch_language(product, "en"):
            product.name = "Test Product"
            product.save()

        # Загружаем продукт один раз
        with self.assertNumQueries(2):
            product = Product.objects.prefetch_related("translations").first()

        # Используем уже загруженный объект — без новых SQL-запросов
        with self.assertNumQueries(0):
            _ = product.safe_translation_getter("name")
