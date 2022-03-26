from rest_framework import permissions

# create permission to authenticate user on get request
class IsAuthenticatedOrCreate(permissions.BasePermission):
    """
    Allows access only to authenticated users or to create new users.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == "GET":
            return True
        return request.user and request.user.is_authenticated
