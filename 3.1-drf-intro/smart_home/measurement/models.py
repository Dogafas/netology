from django.db import models


class Sensor(models.Model):
    name = models.CharField(max_length=50, verbose_name="название", unique=False)
    description = models.CharField(max_length=100, verbose_name="описание")

    class Meta:
        verbose_name = "Датчик"
        verbose_name_plural = "Датчики"

    def __str__(self):
        return self.name


class Measurement(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        verbose_name="датчик",
        related_name="measurements",
    )
    temperature = models.DecimalField(
        max_digits=5, decimal_places=1, default=0.0, verbose_name="температура"
    )
    image = models.ImageField(
        upload_to="measurements/", null=True, blank=True, verbose_name="изображение"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="время обновления")

    class Meta:
        verbose_name = "Измерение"
        verbose_name_plural = "Измерения"
        indexes = [models.Index(fields=["sensor"], name="sensor_idx")]

    def __str__(self):
        return f"{self.sensor.name} - {self.temperature}°C"
