from django.test import TestCase
from django.contrib.auth.models import User
from advertisements.models import Advertisement, AdvertisementStatusChoices
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase


class AdvertisementModelTest(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

        # Создаем тестовое объявление
        self.advertisement = Advertisement.objects.create(
            title="Test Advertisement",
            description="Test Description",
            creator=self.user,
            status=AdvertisementStatusChoices.OPEN,
        )

    def test_advertisement_creation(self):
        # Проверяем, что объявление создано успешно
        self.assertEqual(self.advertisement.title, "Test Advertisement")
        self.assertEqual(self.advertisement.description, "Test Description")
        self.assertEqual(self.advertisement.creator, self.user)
        self.assertEqual(self.advertisement.status, AdvertisementStatusChoices.OPEN)

    def test_advertisement_status_choices(self):
        # Проверяем, что статусы объявления определены правильно
        self.assertEqual(AdvertisementStatusChoices.OPEN, "OPEN")
        self.assertEqual(AdvertisementStatusChoices.CLOSED, "CLOSED")


class AdvertisementViewSetTest(APITestCase):
    def setUp(self):
        # Создаем API client
        self.client = APIClient()

        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpassword", email="admin@example.com"
        )
        # Создаем тестовое объявление
        self.advertisement = Advertisement.objects.create(
            title="Test Advertisement",
            description="Test Description",
            creator=self.user,
            status=AdvertisementStatusChoices.OPEN,
        )

        # Получаем URL для list и create
        self.list_url = reverse(
            "advertisement-list"
        )  # advertisement это name в urls.py
        self.detail_url = reverse(
            "advertisement-detail", args=[self.advertisement.id]
        )  # detail url

    def test_list_advertisements(self):
        # Получаем список объявлений
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_advertisement(self):
        # Авторизуемся как обычный пользователь
        self.client.force_authenticate(user=self.user)

        # Создаем новое объявление
        data = {
            "title": "New Advertisement",
            "description": "New Description",
            "status": AdvertisementStatusChoices.OPEN,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Advertisement.objects.count(), 2)

    def test_update_advertisement_by_author(self):
        # Авторизуемся как автор объявления
        self.client.force_authenticate(user=self.user)

        # Обновляем объявление
        data = {"title": "Updated Advertisement"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Advertisement.objects.get(id=self.advertisement.id).title,
            "Updated Advertisement",
        )

    def test_update_advertisement_by_not_author(self):
        # Создаем другого пользователя
        other_user = User.objects.create_user(
            username="otheruser", password="otherpassword"
        )

        # Авторизуемся как другой пользователь
        self.client.force_authenticate(user=other_user)

        # Пытаемся обновить объявление
        data = {"title": "Updated Advertisement"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, 403)

    def test_delete_advertisement_by_admin(self):
        # Авторизуемся как администратор
        self.client.force_authenticate(user=self.admin_user)

        # Удаляем объявление
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Advertisement.objects.count(), 0)

    def test_create_advertisement_limit(self):
        # Авторизуемся как обычный пользователь
        self.client.force_authenticate(user=self.user)
        # Создаем 9 объявлений
        for i in range(9):
            data = {
                "title": f"Test Advertisement {i}",
                "description": "Test Description",
                "status": AdvertisementStatusChoices.OPEN,
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, 201)
        # Пытаемся создать 10-е объявление
        data = {
            "title": "Test Advertisement 10",
            "description": "Test Description",
            "status": AdvertisementStatusChoices.OPEN,
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["non_field_errors"][0],
            "У вас уже максимум (10) открытых объявлений. Закройте некоторые перед созданием новых.",
        )
