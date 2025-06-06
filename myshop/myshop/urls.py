# # myshop\myshop\urls.py

# from django.conf import settings
# from django.conf.urls.static import static
# from django.conf.urls.i18n import i18n_patterns
# from django.contrib import admin
# from django.urls import include, path
# from django.utils.translation import gettext_lazy as _
# from payment import webhooks
# from payment import views


# urlpatterns = i18n_patterns(
#     path("admin/", admin.site.urls),
#     path(_("cart/"), include("cart.urls", namespace="cart")),
#     path(_("orders/"), include("orders.urls", namespace="orders")),
#     path(_("payment/"), include("payment.urls", namespace="payment")),
#     path(_("coupons/"), include("coupons.urls", namespace="coupons")),
#     path("", include("shop.urls", namespace="shop")),
#     path("__debug__/", include("debug_toolbar.urls")),
# )

# urlpatterns += [
#     path("payment/webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
#     path("payment/webhook/yookassa/", views.yookassa_webhook, name="yookassa-webhook"),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += [path("rosetta/", include("rosetta.urls"))]


from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from payment import webhooks
from payment import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Настройка Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="MyShop API",
        default_version="v1",
        description=_("Multilingual e-commerce API"),
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# API endpoints
api_patterns = [
    path("shop/", include("shop.api.urls")),
    # path("cart/", include("cart.api.urls")),
    # path("orders/", include("orders.api.urls")),
    # path("payment/", include("payment.api.urls")),
    # path("coupons/", include("coupons.api.urls")),
]

urlpatterns = [
    # Админка и веб-интерфейсы
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    # Документация API
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Вебхуки (не требуют перевода)
    path("payment/webhook/", webhooks.stripe_webhook, name="stripe-webhook"),
    path("payment/webhook/yookassa/", views.yookassa_webhook, name="yookassa-webhook"),
]

# Мультиязычные URL (основное приложение)
urlpatterns += i18n_patterns(
    path("", include("shop.urls", namespace="shop")),
    path(_("cart/"), include("cart.urls", namespace="cart")),
    path(_("orders/"), include("orders.urls", namespace="orders")),
    path(_("payment/"), include("payment.urls", namespace="payment")),
    path(_("coupons/"), include("coupons.urls", namespace="coupons")),
    # API с поддержкой языка
    path("api/v1/", include(api_patterns)),
    # Отладка
    path("__debug__/", include("debug_toolbar.urls")),
    prefix_default_language=True,
)

# Отладочные URL только для DEBUG режима
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("rosetta/", include("rosetta.urls"))]
