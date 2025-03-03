from django.urls import reverse
from rest_framework import status
import pytest
from students.models import Course


@pytest.mark.django_db
def test_get_first_course(api_client, courses_factory):
    courses = courses_factory(names=["первый курс"])
    course = courses[0]
    url = reverse("courses-detail", args=[course.id])
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["name"] == "первый курс"


@pytest.mark.django_db
def test_get_courses_list(api_client, courses_factory):
    courses = courses_factory(names=["первый курс", "второй курс"])
    url = reverse("courses-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 2
    assert response_data[0]["name"] == "первый курс"
    assert response_data[1]["name"] == "второй курс"


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, courses_factory):
    courses = courses_factory(names=["первый курс", "второй курс"])
    course1 = courses[0]
    url = reverse("courses-list")
    response = api_client.get(url, data={"id": course1.id})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["name"] == "первый курс"


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, courses_factory):
    courses = courses_factory(names=["первый курс", "второй курс"])
    url = reverse("courses-list") + "?name=первый курс"
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert len(response_data) == 1
    assert response_data[0]["name"] == "первый курс"


@pytest.mark.django_db
def test_create_course(api_client):
    data = {"name": "новый первый курс"}
    url = reverse("courses-list")
    response = api_client.post(url, data=data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Course.objects.count() == 1
    assert Course.objects.first().name == "новый первый курс"


@pytest.mark.django_db
def test_update_course(api_client, courses_factory):
    courses = courses_factory(names=["Оригинальный первый курс"])
    course = courses[0]
    data = {"name": "Обновленный первый курс"}
    url = reverse("courses-detail", args=[course.id])
    response = api_client.put(url, data=data, format="json")
    assert response.status_code == status.HTTP_200_OK
    course.refresh_from_db()
    assert course.name == "Обновленный первый курс"


@pytest.mark.django_db
def test_delete_course(api_client, courses_factory):
    courses = courses_factory(names=["Оригинальный первый курс"])
    course = courses[0]
    url = reverse("courses-detail", args=[course.id])
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Course.objects.count() == 0
