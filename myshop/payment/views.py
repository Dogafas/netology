# myshop/payment/views.py
from decimal import Decimal
import stripe
from yookassa import Configuration, Payment as YooPayment
import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
import logging
from orders.models import Order
from .models import Payment
from .tasks import payment_completed  # Задача остаётся с этим именем
from shop.models import Product
from shop.recommender import Recommender

# Настройка Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

# Настройка ЮKassa
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


# Процесс платежа
def payment_process(request):
    order_id = request.session.get("order_id")
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        payment_method = request.POST.get("payment_method", "stripe")
        success_url = request.build_absolute_uri(
            reverse("payment:payment_success")
        )  # Изменён reverse
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))

        if payment_method == "stripe":
            session_data = {
                "mode": "payment",
                "client_reference_id": order.id,
                "success_url": success_url,
                "cancel_url": cancel_url,
                "line_items": [],
            }
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
            if order.coupon:
                stripe_coupon = stripe.Coupon.create(
                    name=order.coupon.code,
                    percent_off=order.discount,
                    duration="once",
                )
                session_data["discounts"] = [{"coupon": stripe_coupon.id}]
            session = stripe.checkout.Session.create(**session_data)
            Payment.objects.create(
                payment_id=session.id,
                amount=order.get_total_cost(),
                payment_method="stripe",
                order=order,
            )
            return redirect(session.url, code=303)

        elif payment_method == "yookassa":
            idempotence_key = str(uuid.uuid4())
            payment = YooPayment.create(
                {
                    "amount": {
                        "value": str(order.get_total_cost()),
                        "currency": "RUB",
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": success_url,
                    },
                    "capture": True,
                    "description": f"Оплата заказа #{order.id}",
                    "metadata": {"order_id": str(order.id)},
                },
                idempotence_key,
            )
            Payment.objects.create(
                payment_id=payment.id,
                amount=order.get_total_cost(),
                payment_method="yookassa",
                order=order,
            )
            return redirect(payment.confirmation.confirmation_url, code=303)

    return render(request, "payment/process.html", {"order": order})


# Завершение платежа (переименовано)
def payment_success(request):
    return render(request, "payment/completed.html")


# Отмена платежа
def payment_canceled(request):
    return render(request, "payment/canceled.html")


# Обработка вебхуков ЮKassa
@csrf_exempt
def yookassa_webhook(request):
    logger = logging.getLogger(__name__)
    logger.info(f"Webhook request received: {request.method} {request.body}")
    if request.method == "POST":
        try:
            event_json = json.loads(request.body)
            payment_id = event_json["object"]["id"]
            event_type = event_json["event"]
            logger.info(f"Webhook event: {event_type}, payment_id: {payment_id}")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Webhook error: {str(e)}")
            return HttpResponse(status=400)

        if event_type == "payment.succeeded":
            try:
                payment_obj = Payment.objects.get(payment_id=payment_id)
                order = payment_obj.order
                if order and not order.paid:
                    payment_obj.status = "succeeded"
                    order.paid = True
                    order.save()
                    payment_obj.save()
                    product_ids = order.items.values_list("product_id", flat=True)
                    products = Product.objects.filter(id__in=product_ids)
                    r = Recommender()
                    r.products_bought(products)
                    payment_completed.delay(order.id)
            except Payment.DoesNotExist:
                logger.error(f"Payment not found: {payment_id}")
                return HttpResponse(status=404)

        elif event_type == "payment.canceled":
            try:
                payment_obj = Payment.objects.get(payment_id=payment_id)
                payment_obj.status = "canceled"
                payment_obj.save()
            except Payment.DoesNotExist:
                logger.error(f"Payment not found: {payment_id}")
                return HttpResponse(status=404)

        return HttpResponse(status=200)
    logger.warning("Webhook: Not a POST request")
    return HttpResponse(status=400)
