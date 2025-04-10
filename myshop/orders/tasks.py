# myshop\orders\tasks.py
from celery import shared_task
from django.core.mail import send_mail
from .models import Order


@shared_task
#  Отправка письма при успешно созданном заказе
def order_created(order_id):
    order = Order.objects.get(id=order_id)
    subject = f"Заказ # {order.id} создан!"
    message = (
        f"Уважаемый покупатель {order.first_name},\n"
        f"Вы успешно создали заказ,\n"
        f"После оплаты Ваш заказ будет доставлен по адресу {order.address},\n"
        f"Идентификатор Вашего заказа: {order.id}."
    )
    mail_sent = send_mail(subject, message, "admin@myshop.py", [order.email])
    return mail_sent
