from django.contrib import admin
from .models import Sensor, Measurement


class MeasurementInline(admin.TabularInline):
    model = Measurement
    fields = []
    extra = 3


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    list_per_page = 15
    inlines = [MeasurementInline]
    search_fields = ("name",)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    def sensor_name(self, obj):
        return obj.sensor.name

    sensor_name.short_description = "Датчик"

    list_display = ("sensor_name", "temperature", "updated_at")
    list_filter = ("sensor", "updated_at")
    list_per_page = 15
