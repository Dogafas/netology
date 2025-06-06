# myshop\myshop\core\api\base.py
from rest_framework import viewsets
from parler_rest.serializers import TranslatableModelSerializer
from parler_rest.fields import TranslatedFieldsField
from django.utils import translation


class MultilingualSerializer(TranslatableModelSerializer):
    translations = TranslatedFieldsField(shared_model=None)

    class Meta:
        fields = ["id", "translations"]


class MultilingualViewSet(viewsets.ModelViewSet):
    def get_serializer_context(self):
        context = super().get_serializer_context()
        lang = self.request.GET.get("lang") or self.request.META.get(
            "HTTP_ACCEPT_LANGUAGE"
        )
        context["language"] = lang or translation.get_language()
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        lang = self.request.GET.get("lang") or self.request.META.get(
            "HTTP_ACCEPT_LANGUAGE"
        )
        if lang and hasattr(self.queryset.model, "translations"):
            return qs.translated(lang)
        return qs
