from decimal import Decimal
import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from orders.models import Order

# Создание экземпляра Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


# Процесс платежа
def payment_process(request):
    order_id = request.session.get("order_id")
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))

        # Создание сессии Stripe
        session_data = {
            "mode": "payment",
            "client_reference_id": order.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": [],
        }
        # Добавление товаров в сессию Stripe
        for item in order.items.all():
            session_data["line_items"].append(
                {
                    "price_data": {
                        "unit_amount": int(item.price * Decimal("100")),
                        "currency": "RUB",
                        "product_data": {
                            "name": item.product.name,
                        },
                    },
                    "quantity": item.quantity,
                }
            )
        # Выход из сессии Stripe
        session = stripe.checkout.Session.create(**session_data)
        # Перенаправление на страницу оплаты Stripe
        return redirect(session.url, code=303)

    else:
        return render(request, "payment/process.html", locals())


# Завершение платежа
def payment_completed(request):
    return render(request, "payment/completed.html")


# Отмена платежа
def payment_canceled(request):
    return render(request, "payment/canceled.html")
