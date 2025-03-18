from io import BytesIO
import weasyprint
from celery import shared_task
from django.contrib.staticfiles import finders
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.translation import activate
from orders.models import Order


@shared_task
def payment_completed(order_id):
    order = Order.objects.get(id=order_id)
    activate("ru")
    subject = f"Order nr. {order.id}"
    message = (
        f"Dear {order.first_name},\n\n"
        f"You have successfully placed an order."
        f"Your order ID is {order.id}."
    )
    email = EmailMessage(subject, message, "admin@autoparts.com", [order.email])
    html = render_to_string("orders/order/pdf.html", {"order": order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(finders.find("css/pdf.css"))]
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=stylesheets)
    email.attach(f"order_{order.id}.pdf", out.getvalue(), "application/pdf")
    email.send()
