from django.contrib.auth.models import User
from django.forms import ValidationError
from rest_framework import serializers
from advertisements.models import Advertisement, AdvertisementStatusChoices


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
        )


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = (
            "id",
            "title",
            "description",
            "creator",
            "status",
            "created_at",
        )

    def create(self, validated_data):
        """Метод для создания"""

        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""
        user = self.context["request"].user
        # валидация статуса
        if "status" in data and data["status"] not in dict(
            AdvertisementStatusChoices.choices
        ):
            raise ValidationError('Статус должен быть "OPEN" или "CLOSED')

        # валидация заголовка
        if "title" in data and len(data["title"]) < 2:
            raise ValidationError("Заголовок должен быть не менее 2 символов")

        # Валидация лимита открытых объявлений
        if not user.is_staff:
            if "status" in data and data["status"] == AdvertisementStatusChoices.OPEN:
                open_ads_count = Advertisement.objects.filter(
                    creator=user, status=AdvertisementStatusChoices.OPEN
                ).count()
                if open_ads_count >= 10:
                    raise ValidationError(
                        "У вас уже максимум (10) открытых объявлений. Закройте некоторые перед созданием новых."
                    )

        return data
