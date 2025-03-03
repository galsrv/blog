from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS

User = get_user_model()

class IsAuthenticatedOrReadOnlyPlusOwnerControl(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return request.method in SAFE_METHODS or request.user == obj

        return request.method in SAFE_METHODS or request.user == obj.author
    