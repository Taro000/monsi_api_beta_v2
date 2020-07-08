from .serializers import *
from .models import *
from datetime import datetime
from customer_beta import models as customer_models
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import mixins, generics, status, viewsets
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .permissions import *
from stylist_beta.permissions import *
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from rest_framework.authentication import BasicAuthentication
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import django
from rest_framework.parsers import MultiPartParser, JSONParser
from PIL import Image


# ---{General views for REST}------------------------
class CustomerProfileViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsMyCustomerProfile]
        return [permission() for permission in permission_classes]


class ReserveAndHistoryViewSet(viewsets.ModelViewSet):
    queryset = ReserveAndHistory.objects.all()

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsCustomerOwner]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'update' or self.action == 'partial_update':
            return ReserveAndHistoryUpdateSerializer
        else:
            return ReserveAndHistorySerializer

    def destroy(self, request, *args, **kwargs):
        """
        OVERWRITE:
        <Response>
        * Message 'The menu was deleted'
        * Status code '204 No Content'
        """
        return Response(
            data={
                "detail": "メニューは削除されました。",
                "status_code": 204
            }
        )


class TimeslotsViewSet(viewsets.ModelViewSet):
    queryset = Timeslots.objects.all()
    serializer_class = TimeslotsSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsStylistOwner]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        OVERWRITE:
        <Response>
        * Message 'The　timeslot was deleted'
        * Status code '204 No Content'
        """
        return Response(
            data={
                "detail": "タイムスロットは削除されました。",
                "status_code": 204
            }
        )
# ---------------------------------------------------


# ---{For No Logged In Home}-------------------------
class NoLoggedInHomeView(APIView):
    def get_permissions(self):
        """
        OVERWRITE:
        <CHECK: Is http method GET or other?>
        * GET > Give a perm to Anyone
        * Other > Give a perm only to AdminUser
        """
        if self.request.method != 'GET':
            self.permission_classes = [IsAdminUser]
        self.permission_classes = [AllowAny]
        return super(NoLoggedInHomeView, self).get_permissions()

    def get(self, request):
        try:
            catalogs = stylist_models.CatalogImage.objects.all()
            pagenator = Paginator(catalogs, 10)
            page = request.query_params.get('page') or 1
            catalog_contents = HomeCatalogsSerializer(
                pagenator.page(page),
                many=True,
                context={'request': self.request}
            ).data
        except django.core.paginator.EmptyPage:
            page = 1
            catalog_contents = HomeCatalogsSerializer(
                pagenator.page(page),
                many=True,
                context={'request': self.request}
            ).data

        next_api_urls = NoLoggedInHomeNextAPISerializer(NoLoggedInHomeNextAPIs(
            register=reverse(viewname='register',
                             request=request),
        )).data

        return Response(NoLoggedInHomeSerializer(NoLoggedInHomeObject(
            page=page,
            catalogs=catalog_contents,
            next_api=next_api_urls,
        )).data)
# ---------------------------------------------------


# ---{For Home}--------------------------------------
class HomeViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = HomeSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsMyCustomerProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = CustomerProfile.objects.all()
        customer = get_object_or_404(queryset, customer=request.user)
        serializer = HomeSerializer(customer, context={'request': request})
        return Response(serializer.data)
# ---------------------------------------------------


# ---{For Reserves}----------------------------------
class ReservesViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = ReservesSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsMyCustomerProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = CustomerProfile.objects.all()
        customer = get_object_or_404(queryset, customer=request.user)
        serializer = ReservesSerializer(customer, context={'request': request})
        return Response(serializer.data)
# ---------------------------------------------------


# ---{For Logs}--------------------------------------
class LogsViewSet(viewsets.ModelViewSet):
    queryset = CustomerProfile.objects.all()
    serializer_class = LogsSerializer

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = [IsAuthenticated, IsMyCustomerProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = CustomerProfile.objects.all()
        customer = get_object_or_404(queryset, customer=request.user)
        serializer = LogsSerializer(customer, context={'request': request})
        return Response(serializer.data)
# ---------------------------------------------------


# ---{For Setting}-----------------------------------
class SettingViewSet(viewsets.ModelViewSet):
    serializer_class = SettingSerializer
    parser_classes = [MultiPartParser, JSONParser]

    def get_object(self):
        return CustomerProfile.objects.get(customer=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated, IsMyCustomerProfile]
        else:
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = CustomerProfile.objects.all()
        customer = get_object_or_404(queryset, customer=request.user)
        serializer = SettingSerializer(customer, context={'request': request})
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        if request.FILES:
            UPLOAD_DIR = os.path.join(MEDIA_ROOT, 'customer_img')

            uploaded_img = request.FILES.get('img')
            img_name = os.path.join(UPLOAD_DIR, f'{uuid.uuid4()}.jpg')
            uploaded_img.name = img_name
            request.data['img'] = uploaded_img

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
# ---------------------------------------------------
