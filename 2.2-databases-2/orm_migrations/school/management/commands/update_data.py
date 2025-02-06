import json
from django.core.management.base import BaseCommand
from school.models import Student, Teacher


class Command(BaseCommand):
    help = 'Обновляет связи между студентами и учителями на основе данных из school.json'

    def handle(self, *args, **options):
        """Выполняет логику команды."""

        with open('school.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data:
            if item['model'] == 'school.student':
                student_id = item['pk']
                teacher_id = item['fields']['teacher']  # Получаем ID учителя из старой структуры

                try:
                    student = Student.objects.get(pk=student_id)
                    teacher = Teacher.objects.get(pk=teacher_id)

                    student.teachers.clear()
                    student.teachers.add(teacher)  # Добавляем учителя к студенту
                    self.stdout.write(self.style.SUCCESS(f"Студент {student.name} добавлен к учителю {teacher.name}")) 

                except Student.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Студент с ID {student_id} не найден.")) 
                except Teacher.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Учитель с ID {teacher_id} не найден.")) 
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Произошла ошибка при обработке студента {student_id}: {e}")) 

        self.stdout.write(self.style.SUCCESS("Обновление данных завершено.")) 