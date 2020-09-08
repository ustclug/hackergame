from rest_framework import permissions

from group.models import Application


class IsInGroup(permissions.BasePermission):
    message = '必须为组内成员'

    def has_object_permission(self, request, view, obj):
        return request.user in obj.users


class IsGroupAdmin(permissions.BasePermission):
    message = '必须为组管理员'

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Application):
            return request.user in obj.group.admin.all()
        return request.user in obj.admin.all()


class IsGroupAdminOrReadOnly(permissions.BasePermission):
    message = '必须为组管理员'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user in obj.admin.all()
