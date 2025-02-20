from rest_framework import serializers
from .models import Measurement, Sensor


# TODO: опишите необходимые сериализаторы
class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ["id", "name", "description"]


class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ["id", "sensor", "temperature", "image", "updated_at", "created_at"]
        read_only_fields = ["updated_at", "created_at"]
