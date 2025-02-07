from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet
from .models import Article, Tag, Scope


class ScopeInlineFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            # форма не пустая и не будет удалена
            if form.is_valid() and not form.cleaned_data.get('DELETE', False): # ("Убираем проверку на form.has_changed()")
                if form.cleaned_data.get('is_main'): #  ("Безопасный доступ к is_main")
                    count += 1

        if count == 0: #  ("Если нет ни одного основного тега")
            raise ValidationError('Укажите основной раздел') #  ("Выводим ошибку")
        if count > 1: #  ("Если больше одного основного тега")
            raise ValidationError('Основным может быть только один раздел') #  ("Выводим ошибку")
        return self.cleaned_data  #  ("Возвращаем очищенные данные")


class ScopeInline(admin.TabularInline):
    model = Scope
    formset = ScopeInlineFormset #  ("Указываем formset для валидации")
    extra = 0 #  ("Убираем лишние пустые формы")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines = [ScopeInline] #  ("Добавляем inline для работы с промежуточной моделью Scope")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass #  ("Простая регистрация модели Tag")