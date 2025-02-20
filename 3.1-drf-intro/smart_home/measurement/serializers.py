from rest_framework import serializers

from smart_home.measurement.models import Measurement, Sensor


# TODO: опишите необходимые сериализаторы
class MeasurementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measurement
        fields = ["temperature", "updated_at"]


class SensorDetailSerializer(serializers.ModelSerializer):
    measurement = MeasurementSerializer(many=True, read_only=True)

    class Meta:
        model = Sensor
        fields = ["name", "description", "measurement"]
