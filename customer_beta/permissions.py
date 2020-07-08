from rest_framework import permissions


class IsMyCustomerProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user


class IsCustomerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer.customer == request.user
