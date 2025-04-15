# myshop\shop\views.py
from cart.forms import CartAddProductForm
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .filters import ProductFilter
from .recommender import Recommender
from .models import Category, Product
from django.conf import settings
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import CategorySerializer, ProductSerializer


def product_list(request, category_slug=None):
    category = None
    # Получаем все категории с учетом текущего языка
    categories = Category.objects.all()
    products = Product.objects.filter(available=True).order_by("id")

    if category_slug:
        language = request.LANGUAGE_CODE
        try:
            category = get_object_or_404(
                Category,
                translations__language_code=language,
                translations__slug=category_slug,
            )
        except Category.DoesNotExist:
            # Пробуем запасной язык, если текущего нет
            fallback_language = settings.PARLER_LANGUAGES["default"]["fallback"]
            category = get_object_or_404(
                Category,
                translations__language_code=fallback_language,
                translations__slug=category_slug,
            )
        products = products.filter(category=category)

    paginator = Paginator(products, 6)
    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(
        request,
        "shop/product/list.html",
        {"category": category, "categories": categories, "products": products},
    )


def product_detail(request, id, slug):
    language = request.LANGUAGE_CODE
    try:
        product = get_object_or_404(
            Product.objects.select_related("category").prefetch_related("images"),
            id=id,
            translations__language_code=language,
            translations__slug=slug,
            available=True,
        )
    except Product.DoesNotExist:
        # Пробуем запасной язык
        fallback_language = settings.PARLER_LANGUAGES["default"]["fallback"]
        product = get_object_or_404(
            Product.objects.select_related("category").prefetch_related("images"),
            id=id,
            translations__language_code=fallback_language,
            translations__slug=slug,
            available=True,
        )
    cart_product_form = CartAddProductForm()
    try:
        r = Recommender()
        recommended_products = r.suggest_products_for([product], 4)
        recommended_products = (
            Product.objects.filter(id__in=[p.id for p in recommended_products])
            .select_related("category")
            .prefetch_related("images")
        )
    except Exception as e:
        print(f"Error in recommender: {e}")

    return render(
        request,
        "shop/product/detail.html",
        {
            "product": product,
            "cart_product_form": cart_product_form,
            "recommended_products": recommended_products,
        },
    )


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
