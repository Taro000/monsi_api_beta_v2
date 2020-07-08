from rest_framework import permissions


class IsMyStylistProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.stylist == request.user


class IsStylistOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.stylist.stylist == request.user


class IsCatalogOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.menu.stylist.stylist == request.user


class IsMe(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user
