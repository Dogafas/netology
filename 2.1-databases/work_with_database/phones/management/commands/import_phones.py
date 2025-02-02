import csv
from django.core.management.base import BaseCommand
from phones.models import Phone

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        with open('phones.csv', 'r', encoding='utf-8') as file:
            phones = list(csv.DictReader(file, delimiter=';'))

        for phone_data in phones:
            try:
                phone = Phone(
                    name=phone_data['name'],
                    image=phone_data['image'],
                    price=phone_data['price'],
                    release_date=phone_data['release_date'],
                    lte_exists=phone_data['lte_exists'] == 'True',
                    
                )
                phone.save()
                self.stdout.write(self.style.SUCCESS(f'Телефон "{phone.name}" успешно импортирован'))
            except Exception as e:
                 self.stdout.write(self.style.ERROR(f'Ошибка импорта телефона: {phone_data.get("name", "N/A")}, ошибка: {e}'))