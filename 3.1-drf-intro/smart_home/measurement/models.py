from django.db import models


# модели датчика (Sensor) и измерения (Measurement)
class Sensor(models.Model):
    name = models.CharField(max_length=50, verbose_name="название")
    description = models.CharField(max_length=100, verbose_name="описание")

    class Meta:
        verbose_name = "Датчик"
        verbose_name_plural = "Датчики"

    def __str__(self):
        return self.name


class Measurement(models.Model):
    id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, verbose_name="датчик")
    temperature = models.DecimalField(
        max_digits=2, decimal_places=1, default=0.0, verbose_name="температура"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="время обновления")

    class Meta:
        verbose_name = "Измерение"
        verbose_name_plural = "Измерения"

    def __str__(self):
        return f"{self.sensor.name} - {self.temperature}°C"
