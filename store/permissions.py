from rest_framework import permissions 
from rest_framework.permissions import SAFE_METHODS

import copy


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.methods in SAFE_METHODS or (request.user and request.user.is_staff))

class SendPrivateEmailToCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.has_perm('store.send_private_email'))

class CustomDjangoModelPermissions(permissions.BasePermission):
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']

