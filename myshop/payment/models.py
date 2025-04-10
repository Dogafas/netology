# payment/models.py
from django.db import models
import uuid


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("stripe", "Stripe"),
        ("yookassa", "ЮKassa"),
    )

    payment_id = models.CharField(
        max_length=255, unique=True, default=uuid.uuid4, editable=False
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="pending")
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHODS, default="stripe"
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.payment_method} Payment {self.payment_id} - {self.amount}"
