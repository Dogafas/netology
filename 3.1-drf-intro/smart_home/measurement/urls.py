from django.urls import path

from . import views


urlpatterns = [
    # TODO: зарегистрируйте необходимые маршруты
    path('sensors/', views.SensorListCreateView.as_view(), name='sensor-list-create'),
    path('sensors/<int:pk>/', views.SensorDetailView.as_view(), name='sensor-detail'),
    path('measurements/', views.MeasurementListCreateView.as_view(), name='measurement-create'),

]
