# myshop\core\api\mixins.py
from django.utils import translation


class LanguageContextMixin:
    def get_serializer_context(self):
        context = super().get_serializer_context()
        lang = self.request.GET.get("lang") or self.request.META.get(
            "HTTP_ACCEPT_LANGUAGE"
        )
        context["language"] = lang or translation.get_language()
        return context
