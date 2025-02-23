from django.contrib import admin
from .models import Product, Stock, StockProduct


# Регистрация модели Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "description")  # Поля, отображаемые в списке
    search_fields = ("title",)  # Поля для поиска
    list_filter = ("title",)  # Фильтры в боковой панели
    ordering = ("title",)  # Сортировка по умолчанию


# Регистрация модели Stock
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = (
        "address",
        "products_count",
    )  # Отображение адреса и количества продуктов
    search_fields = ("address",)  # Поиск по адресу

    def products_count(self, obj):
        return obj.products.count()

    products_count.short_description = "Количество продуктов"  # Название столбца


# Настройка для связи многие-ко-многим через StockProduct
class StockProductInline(admin.TabularInline):
    model = StockProduct
    extra = 1  # Количество пустых форм для добавления
    min_num = 1  # Минимальное количество форм


# Регистрация модели StockProduct
@admin.register(StockProduct)
class StockProductAdmin(admin.ModelAdmin):
    list_display = ("stock", "product", "quantity", "price")  # Поля в списке
    list_filter = ("stock", "product")  # Фильтры
    search_fields = ("stock__address", "product__title")  # Поиск по связанным полям
    list_editable = ("quantity", "price")  # Редактируемые поля прямо в списке


# Добавляем inline в StockAdmin для удобного редактирования связанных StockProduct
StockAdmin.inlines = [StockProductInline]
