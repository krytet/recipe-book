from rest_framework.permissions import BasePermission


class CustomUserPermission(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.is_anonymous:
            return True
        elif request.method == 'GET':
            if request.user.is_authenticated:
                return True
            else:
                if view.action == 'retrieve':
                    return False
                else:
                    return True
        return False
