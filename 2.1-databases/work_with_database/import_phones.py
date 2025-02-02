import os
import csv
import django
from datetime import datetime

# Указываем Django использовать настройки нашего проекта
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "work_with_database.settings")
django.setup()

from phones.models import Phone

def import_phones_from_csv(csv_file_path):
    """Импортирует данные из CSV-файла в модель Phone."""
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            try:
                # Преобразование типов данных
                id_value = int(row['id']) 
                price_value = float(row['price'])
                release_date_value = datetime.strptime(row['release_date'], '%Y-%m-%d').date()
                lte_exists_value = bool(row['lte_exists'].lower() == 'true')

                # Создание и сохранение объекта Phone
                Phone.objects.create(
                    id=id_value,
                    name=row['name'],
                    image=row['image'],
                    price=price_value,
                    release_date=release_date_value,
                    lte_exists=lte_exists_value
                )
                print(f"Телефон '{row['name']}' успешно импортирован.")
            except Exception as e:
                print(f"Ошибка импорта телефона '{row.get('name', 'неизвестно')}': {e}")

if __name__ == "__main__":
    csv_file = 'phones.csv' # <-ЗДЕСЬ ИЗМЕНЕНИЯ: ("Замени 'phones.csv' на путь к твоему файлу, если он не в корне проекта")
    import_phones_from_csv(csv_file)
    print("Импорт завершен.")