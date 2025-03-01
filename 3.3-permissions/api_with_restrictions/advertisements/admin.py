from django.contrib import admin
from advertisements.models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    """Настройка отображения модели Advertisement в админ-панели."""

    # Количество записей на странице
    list_per_page = 20

    # Поля, отображаемые в списке
    list_display = ("id", "title", "creator", "status", "created_at", "updated_at")

    # Фильтры в боковой панели
    list_filter = ("status", "created_at", "updated_at", "creator")

    # Поле для поиска
    search_fields = ("title", "description")

    # Поля, доступные для редактирования в списке
    list_editable = ("status",)  # можно менять статус прямо в списке

    # Детальная информация при просмотре записи
    fields = ("title", "description", "status", "creator", "created_at", "updated_at")

    # Поля, доступные только для чтения
    readonly_fields = ("creator", "created_at", "updated_at")
