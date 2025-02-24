from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from phonenumbers import parse, is_valid_number, NumberParseException
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from coupons.models import Coupon


class Order(models.Model):
    """информация о заказе и связанных с ним данных"""

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(
        Coupon,
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    discount = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["-created"]),
        ]

    def __str__(self):
        return f"Заказ № {self.id}"

    def get_total_cost(self):
        total_cost = self.get_total_cost_before_discount()
        return total_cost - self.get_discount()

    def clean(self):
        super().clean()
        # Проверка телефона
        if self.phone:
            try:
                phone_obj = parse(self.phone, "RU")  # Проверяем в регионе Россия
                if not is_valid_number(phone_obj):
                    raise ValidationError(
                        {"phone": "Введите корректный номер телефона."}
                    )
            except NumberParseException:
                raise ValidationError({"phone": "Введите корректный номер телефона."})

    def get_stripe_url(self):
        # для отличия тестовой среды от продакшена
        if not self.stripe_id:
            return ""
        if "__test__" in settings.STRIPE_SECRET_KEY:
            path = "/test/"
        else:
            path = "/"
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"

    def get_total_cost_before_discount(self):
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self):
        total_cost = self.get_total_cost_before_discount()
        if self.discount:
            return total_cost * (self.discount / Decimal(100))
        return Decimal(0)


class OrderItem(models.Model):
    """описывает отдельный товар в заказе"""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(
        "shop.Product", related_name="order_items", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
