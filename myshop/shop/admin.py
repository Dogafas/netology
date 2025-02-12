from django.contrib import admin
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display =['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 8

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 8

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'price', 'available', 'created', 'updated']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 8
    inlines = [ProductImageInline]

