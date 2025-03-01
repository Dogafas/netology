from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from advertisements.models import Advertisement
from advertisements.filters import AdvertisementFilter
from advertisements.serializers import AdvertisementSerializer
from advertisements.permissions import IsAdvertisementAuthor, IsAdminOrReadOnly


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filterset_class = AdvertisementFilter
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        """Получение прав для действий."""
        if self.request.user.is_staff:
            return [IsAuthenticated(), IsAdminOrReadOnly()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdvertisementAuthor()]
        elif self.action == "create":
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        """Фильтрация кверисета по умолчанию (опционально)."""
        print(f"Query params: {self.request.query_params}")
        return Advertisement.objects.all()
