from rest_framework import permissions


class IsAdvertisementAuthor(permissions.BasePermission):
    """Проверка, что пользователь является автором объявления."""

    def has_object_permission(self, request, view, obj):
        # Разрешение на безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для update, partial_update и destroy проверяем, что пользователь — автор
        return obj.creator == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ на запись только администраторам,
    всем остальным - только на чтение.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff
