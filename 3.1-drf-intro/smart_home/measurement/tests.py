import json
from dotenv import load_dotenv
import os
import io

from django.test import TransactionTestCase
from django.urls import reverse
from django.core.files.uploadedfile import (
    SimpleUploadedFile,
)
from PIL import Image

load_dotenv()

# Получаем URL сервера из переменных окружения, или используем значение по умолчанию
SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000/api")


class SensorTests(TransactionTestCase):
    def test_create_sensor(self):
        """
        Тест создания датчика.
        """
        url = reverse("sensor-list-create")
        data = {"name": "Test Sensor", "description": "Test Description"}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

        # Проверяем, что запрос был успешным
        self.assertEqual(response.status_code, 201)

        # Проверяем, что в ответе содержится правильный JSON
        response_json = response.json()

        # Проверяем, что имя датчика в ответе соответствует отправленному имени
        self.assertEqual(response_json["name"], "Test Sensor")

        # Проверяем, что ID датчика был сгенерирован
        self.assertTrue("id" in response_json)

    def test_update_sensor(self):
        """
        Тест изменения датчика.
        """
        # Сначала создадим датчик, который будем обновлять
        url_create = reverse("sensor-list-create")
        data_create = {"name": "Initial Sensor", "description": "Initial Description"}
        response_create = self.client.post(
            url_create, data=json.dumps(data_create), content_type="application/json"
        )
        self.assertEqual(response_create.status_code, 201)
        sensor_id = response_create.json()["id"]

        # Теперь обновим этот датчик
        url_update = reverse("sensor-detail", kwargs={"pk": sensor_id})
        data_update = {"name": "Updated Sensor", "description": "Updated Description"}
        response_update = self.client.patch(
            url_update, data=json.dumps(data_update), content_type="application/json"
        )
        self.assertEqual(response_update.status_code, 200)
        self.assertEqual(response_update.json()["name"], "Updated Sensor")

    def test_add_measurement(self):
        """
        Тест добавления измерения.
        """
        # Сначала создадим датчик, к которому будем добавлять измерение
        url_create = reverse("sensor-list-create")
        data_create = {"name": "Sensor for Measurement", "description": "Description"}
        response_create = self.client.post(
            url_create, data=json.dumps(data_create), content_type="application/json"
        )
        self.assertEqual(response_create.status_code, 201)
        sensor_id = response_create.json()["id"]

        # Теперь добавим измерение к этому датчику
        url_add_measurement = reverse("measurement-create")
        data_add_measurement = {"sensor": sensor_id, "temperature": 25.5}
        response_add_measurement = self.client.post(
            url_add_measurement,
            data=json.dumps(data_add_measurement),
            content_type="application/json",
        )
        self.assertEqual(response_add_measurement.status_code, 201)
        self.assertEqual(float(response_add_measurement.json()["temperature"]), 25.5)

    def test_get_sensors_list(self):
        """
        Тест получения списка датчиков.
        """
        # Сначала создадим несколько датчиков
        url_create = reverse("sensor-list-create")
        data_create1 = {"name": "Sensor 1", "description": "Description 1"}
        data_create2 = {"name": "Sensor 2", "description": "Description 2"}
        self.client.post(
            url_create, data=json.dumps(data_create1), content_type="application/json"
        )
        self.client.post(
            url_create, data=json.dumps(data_create2), content_type="application/json"
        )

        # Получаем список датчиков
        url_get_list = reverse("sensor-list-create")
        response_get_list = self.client.get(url_get_list)
        self.assertEqual(response_get_list.status_code, 200)
        self.assertGreaterEqual(
            len(response_get_list.json()), 2
        )  # Проверяем, что в списке хотя бы 2 датчика

    def test_get_sensor_detail(self):
        """
        Тест получения информации по конкретному датчику.
        """
        # Сначала создадим датчик
        url_create = reverse("sensor-list-create")
        data_create = {"name": "Detailed Sensor", "description": "Detailed Description"}
        response_create = self.client.post(
            url_create, data=json.dumps(data_create), content_type="application/json"
        )
        self.assertEqual(response_create.status_code, 201)
        sensor_id = response_create.json()["id"]

        # Получаем информацию по конкретному датчику
        url_get_detail = reverse("sensor-detail", kwargs={"pk": sensor_id})
        response_get_detail = self.client.get(url_get_detail)
        self.assertEqual(response_get_detail.status_code, 200)
        self.assertEqual(response_get_detail.json()["name"], "Detailed Sensor")

    def test_add_measurement_with_image(
        self,
    ):
        """
        Тест добавления измерения с изображением.
        """
        # Сначала создадим датчик, к которому будем добавлять измерение
        url_create = reverse("sensor-list-create")
        data_create = {"name": "Sensor with Image", "description": "Description"}
        response_create = self.client.post(
            url_create, data=json.dumps(data_create), content_type="application/json"
        )
        self.assertEqual(response_create.status_code, 201)
        sensor_id = response_create.json()["id"]

        # Создаем тестовое изображение
        image = Image.new("RGB", (100, 100), color="white")
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)

        # Создаем SimpleUploadedFile
        image_file = SimpleUploadedFile(
            "test_image.jpg", image_io.read(), content_type="image/jpeg"
        )

        # Теперь добавим измерение с изображением к этому датчику
        url_add_measurement = reverse("measurement-create")
        data_add_measurement = {
            "sensor": sensor_id,
            "temperature": 25.5,
            "image": image_file,
        }
        response_add_measurement = self.client.post(
            url_add_measurement, data=data_add_measurement, format="multipart"
        )
        self.assertEqual(response_add_measurement.status_code, 201)
