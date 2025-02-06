from django.views.generic import ListView
from django.shortcuts import render

from .models import Student


def students_list(request):
    template = 'school/students_list.html'
    students = Student.objects.all().order_by('group').prefetch_related('teachers')
    context = {'object_list': students}
    return render(request, template, context)

    # используйте этот параметр для упорядочивания результатов
    # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.query.QuerySet.order_by
    # This document is for an insecure version of Django that is no longer supported. Please upgrade to a newer release!!!! (обновите материал)

    # ordering = 'group'    
