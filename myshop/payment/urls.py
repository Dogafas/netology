# myshop/payment/urls.py
from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("process/", views.payment_process, name="process"),
    path("success/", views.payment_success, name="payment_success"),
    path("canceled/", views.payment_canceled, name="canceled"),
]
