from django.contrib import admin
from .models import Phone

@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "image", "release_date", "lte_exists")
    search_fields = ("lte_exists",)
    list_filter = ("name", )