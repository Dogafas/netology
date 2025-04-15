# myshop/shop/admin.py
from django.contrib import admin
from .models import Category, Product, ProductImage
from parler.admin import TranslatableAdmin
from django.utils.html import format_html


# --- Вспомогательная функция для генерации превью ---
def create_image_preview(
    image_field, width=50, height=50, default_text="Нет изображения"
):
    """
    Генерирует HTML-код для превью изображения в админке.
    """
    if image_field and hasattr(image_field, "url"):  # Проверяем наличие поля и URL
        # Используем image_field.url, который уже учитывает MEDIA_URL
        return format_html(
            '<img src="{}" width="{}" height="{}" style="object-fit: contain;" />',
            image_field.url,
            width,
            height,
        )
    return default_text


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ["name", "slug"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}

    list_per_page = 8


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 7
    readonly_fields = ["image_tag"]

    def image_tag(self, obj):
        # Вызываем вспомогательную функцию с нужными размерами
        return create_image_preview(obj.image, height=35, width=35)

    image_tag.short_description = "Превью"


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = [
        "name",
        "main_image_preview",
        "price",
        "available",
        "slug",
        "created",
        "updated",
    ]
    list_filter = ["available", "created", "updated", "category"]
    list_editable = ["price", "available"]

    def get_prepopulated_fields(self, request, obj=None):
        return {"slug": ("name",)}

    list_per_page = 8
    inlines = [ProductImageInline]

    def main_image_preview(self, obj):
        return create_image_preview(obj.image)

    main_image_preview.short_description = "Основное фото"
