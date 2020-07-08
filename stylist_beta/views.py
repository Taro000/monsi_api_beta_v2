from .serializers import *
from .models import *
from datetime import datetime
from customer_beta import models as customer_models
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import mixins, generics, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .permissions import *
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import BasicAuthentication
from django.shortcuts import get_object_or_404
import os
from monsiApiRehearsalBetaV2.settings import MEDIA_ROOT
import uuid
from rest_framework.parsers import MultiPartParser, JSONParser


header_dict = {
    'Content-Type': 'application/json',
    'X-Content-Type-Options': 'nosniff'
}


# ---{General views for REST}------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy' or self.action == 'create':
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsMe]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, headers=header_dict)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, headers=header_dict)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class StylistProfileViewSet(viewsets.ModelViewSet):
    queryset = StylistProfile.objects.all()
    serializer_class = StylistProfileSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsStylistOwner]
        return [permission() for permission in permission_classes]


class ProblemViewSet(viewsets.ModelViewSet):
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [IsAdminUser]


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsStylistOwner]
        return [permission() for permission in permission_classes]


class CatalogImageViewSet(viewsets.ModelViewSet):
    queryset = CatalogImage.objects.all()
    serializer_class = CatalogImageSerializer
    parser_classes = [MultiPartParser, JSONParser]

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsCatalogOwner]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        共和国後のTODO:
        request.FILESがないときに MultiValueDictKeyError(key)は起きるが、
        適切なJson形式の例外レスポンスを返せていないので、その処理を書く。
        """
        if request.FILES["before_img"]:
            UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'before_img')

            uploaded_before = request.FILES.get('before_img')
            before_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
            uploaded_before.name = before_name
            request.data['before_img'] = uploaded_before
        else:
            request.data['before_img'] = None

        if request.FILES["after_img"]:
            UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'after_img')

            uploaded_after = request.FILES.get('after_img')
            after_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
            uploaded_after.name = after_name
            request.data['after_img'] = uploaded_after
        else:
            request.data['after_img'] = None

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if request.FILES:
            if request.FILES['before_img']:
                UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'before_img')

                uploaded_img = request.FILES.get('before_img')
                img_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
                uploaded_img.name = img_name
                request.data['before_img'] = uploaded_img

            if request.FILES['after_img']:
                UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'after_img')

                uploaded_img = request.FILES.get('after_img')
                img_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
                uploaded_img.name = img_name
                request.data['after_img'] = uploaded_img

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        OVERRIDE:
        <Response>
        * Message 'The B/A image was deleted'
        * Status code '204 No Content'
        """
        return Response(
            data={
                "detail": "Before/After画像は削除されました。",
                "status_code": 204
            }
        )
# ---------------------------------------------------


# ---{for Home}--------------------------------------
class HomeViewSet(viewsets.ModelViewSet):
    queryset = StylistProfile.objects.all()
    serializer_class = HomeSerializer
    parser_classes = [MultiPartParser, JSONParser]

    def get_object(self):
        return StylistProfile.objects.get(stylist=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsMyStylistProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(stylist=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = StylistProfile.objects.all()
        serializer = HomeSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = StylistProfile.objects.all()
        stylist = get_object_or_404(queryset, stylist=request.user)
        serializer = HomeSerializer(stylist, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if request.FILES:
            if request.FILES['img']:
                UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'stylist_img')

                uploaded_img = request.FILES.get('img')
                img_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
                uploaded_img.name = img_name
                request.data['img'] = uploaded_img
            if request.FILES['salon_img']:
                UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'salon_img')

                uploaded_img = request.FILES.get('salon_img')
                img_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
                uploaded_img.name = img_name
                request.data['salon_img'] = uploaded_img

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
# ---------------------------------------------------


# ---{For Edit-Catalogs}-----------------------------
class EditCatalogsViewSet(viewsets.ModelViewSet):
    queryset = StylistProfile.objects.all()
    serializer_class = EditCatalogsSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsMyStylistProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = StylistProfile.objects.all()
        stylist = get_object_or_404(queryset, stylist=request.user)
        serializer = EditCatalogsSerializer(stylist, context={'request': request})
        return Response(serializer.data)


# ---------------------------------------------------


# ---{For Schedule}----------------------------------
class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = StylistProfile.objects.all()
    serializer_class = ScheduleSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsMyStylistProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = StylistProfile.objects.all()
        stylist = get_object_or_404(queryset, stylist=request.user)
        serializer = ScheduleSerializer(stylist, context={'request': request})
        return Response(serializer.data)


# ---------------------------------------------------


# ---{Auth-token}------------------------------------
class CustomAuthToken(ObtainAuthToken):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key
        })
# ---------------------------------------------------


# ---{Register}--------------------------------------
class RegisterViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# ----------------------------------------------------
