# TODO: опишите необходимые обработчики, рекомендуется использовать generics APIView классы:
# TODO: ListCreateAPIView, RetrieveUpdateAPIView, CreateAPIView
from rest_framework import generics

from .serializers import MeasurementSerializer, SensorSerializer
from .models import Sensor, Measurement


class SensorListCreateView(generics.ListCreateAPIView):
    queryset = Sensor.objects.all().order_by("id")
    serializer_class = SensorSerializer


class MeasurementListCreateView(generics.ListCreateAPIView):
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer


class SensorDetailView(generics.RetrieveUpdateAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
