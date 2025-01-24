from django.shortcuts import render, redirect
from django.urls import reverse
import csv
from django.conf import settings
from django.core.paginator import Paginator 
from django.shortcuts import render, redirect
from django.urls import reverse

def index(request):
    return redirect(reverse('bus_stations'))


def bus_stations(request):
    # Шаг 1: Чтение данных из CSV
    with open(settings.BUS_STATION_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f) 
        bus_stations_data = list(reader) 

    # Шаг 2: Пагинация
    page_number = request.GET.get('page') 
    paginator = Paginator(bus_stations_data, 10) 
    page = paginator.get_page(page_number)

    # Шаг 3: Формирование контекста
    context = {
        'bus_stations': page.object_list, 
        'page': page,
        'paginator': paginator, 
    }
    return render(request, 'stations/index.html', context)