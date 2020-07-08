from .models import *
from rest_framework import serializers, status
from django.core.paginator import Paginator
from customer_beta import models as customer_models
from rest_framework.reverse import reverse
from datetime import datetime
from django.db.models import Avg
from django.contrib.auth import authenticate, password_validation
from django.core.paginator import Paginator
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from drf_extra_fields.fields import DateTimeRangeField
from django.utils import timezone
import pytz
from stylist_beta.utils import CustomValidation
import django
import os
from monsiApiRehearsalBetaV2.settings import MEDIA_ROOT
from PIL import Image


# ---{General serializers for REST}------------------
# ---{REST CustomerProfile API}----------------------
class CustomerProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'id',
            'username',
            'img',
            'age',
            'gender',
            'phone_number',
        )
        read_only_fields = (
            'id',
            'username',
        )

    def get_id(self, instance):
        return instance.customer.id

    def get_username(self, instance):
        return instance.customer.username
# ---------------------------------------------------


# ---{REST ReserveAndHistory API}--------------------
class ReserveAndHistorySerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    stylist_name = serializers.SerializerMethodField()
    menu_name = serializers.SerializerMethodField()
    time = DateTimeRangeField()

    class Meta:
        model = ReserveAndHistory
        fields = (
            'id',
            'customer',
            'stylist',
            'time',
            'menu',
            'rating',
            'customer_name',
            'stylist_name',
            'menu_name',
        )
        read_only_fields = (
            'id',
            'customer_name',
            'stylist_name',
            'menu_name',
        )
        extra_kwargs = {
            'customer': {'write_only': True},
            'stylist': {'write_only': True},
            'menu': {'write_only': True},
        }

    def get_customer_name(self, instance):
        return instance.customer.customer.last_name + ' ' + instance.customer.customer.first_name

    def get_stylist_name(self, instance):
        return instance.stylist.stylist.last_name + ' ' + instance.stylist.stylist.first_name

    def get_menu_name(self, instance):
        return instance.menu.menu_name


class RangeSerializer(serializers.ModelSerializer):
    time = DateTimeRangeField()

    class Meta:
        model = ReserveAndHistory
        fields = ('time',)


class ReserveAndHistoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReserveAndHistory
        fields = ('rating',)

    def update(self, instance, validated_data):
        """
        OVERWRITE:
        <Field>
        *rating
        <CHECK: object is reserve or history?>
        *reserve > Save a change
        *history > Raise Validation Error
        """
        range = RangeSerializer(instance).data

        if datetime.strptime(range['time']['lower'], '%Y-%m-%dT%H:%M:%S%z') < pytz.utc.localize(timezone.datetime.now()):
            instance.rating = validated_data.get('rating', instance.rating)
            instance.save()
            return instance
        else:
            raise CustomValidation('予約情報は変更できません。キャンセル後、再予約してください。', status.HTTP_400_BAD_REQUEST)
# ---------------------------------------------------


# ---{REST Timeslots API}----------------------------
class TimeslotsSerializer(serializers.ModelSerializer):
    stylist_name = serializers.SerializerMethodField()

    class Meta:
        model = Timeslots
        fields = (
            'time',
            'stylist_name',
        )
        read_only_fields = ('id',)

    def get_stylist_name(self, instance):
        return instance.stylist.stylist.last_name + ' ' + instance.stylist.stylist.first_name
# ---------------------------------------------------
# ---------------------------------------------------


# ---{Home(No Logged In)}----------------------------
class HomeStylistProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = stylist_models.StylistProfile
        fields = (
            'year',
            'salon_name',
            'place',
            'access',
            'salon_img',
        )


class HomeMenuSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = stylist_models.Menu
        fields = (
            'menu_name',
            'img',
            'price',
            'time',
        )


class HomeTimeslotsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timeslots
        fields = ('time',)


class HomeCatalogsSerializer(serializers.ModelSerializer):
    stylist_name = serializers.SerializerMethodField()
    rating_average = serializers.SerializerMethodField()
    stylist_info = serializers.SerializerMethodField()
    menus = serializers.SerializerMethodField()
    timeslots = serializers.SerializerMethodField()

    class Meta:
        model = stylist_models.CatalogImage
        fields = (
            'before_img',
            'after_img',
            'stylist_name',
            'rating_average',
            'stylist_info',
            'menus',
            'timeslots',
        )

    def get_stylist_name(self, instance):
        return instance.menu.stylist.stylist.last_name + ' ' + instance.menu.stylist.stylist.first_name

    def get_rating_average(self, instance):
        try:
            menus = stylist_models.Menu.objects.filter(stylist=instance.menu.stylist).all()
            rating_average = ReserveAndHistory.objects.filter(
                menu__in=menus,
                time__endswith__lt=timezone.datetime.now()
            ).all().aggregate(Avg('rating'))
            return rating_average['rating__avg']
        except:
            rating_average = None
            return rating_average

    def get_stylist_info(self, instance):
        try:
            stylist_info = HomeStylistProfileSerializer(
                stylist_models.StylistProfile.objects.get(stylist=instance.menu.stylist)
            ).data
            return stylist_info
        except:
            stylist_info = None
            return stylist_info

    def get_menus(self, instance):
        try:
            menu_contents = HomeMenuSerializer(
                stylist_models.Menu.objects.filter(stylist=instance.menu.stylist).all(),
                many=True,
                context=self.context
            ).data
            return menu_contents
        except:
            menu_contents = None
            return menu_contents

    def get_timeslots(self, instance):
        try:
            timeslots = Timeslots.objects.filter(
                stylist=instance.menu.stylist,
                time__endswith__gte=timezone.datetime.now(),
            ).all().order_by('time__startswith')
            pagenator = Paginator(timeslots, 10)
            page = self.context['request'].query_params.get('timeslots_page') or 1
            timeslot_contents = HomeTimeslotsSerializer(pagenator.page(page), many=True).data
            return timeslot_contents
        except django.core.paginator.EmptyPage:
            page = 1
            timeslot_contents = HomeTimeslotsSerializer(pagenator.page(page), many=True).data
            return timeslot_contents


class NoLoggedInHomeNextAPIs(object):
    def __init__(self, register):
        self.register = register


class NoLoggedInHomeNextAPISerializer(serializers.Serializer):
    register = serializers.URLField()


class NoLoggedInHomeObject(object):
    def __init__(self, page, catalogs, next_api):
        self.page = page
        self.catalogs = catalogs
        self.next_api = next_api


class NoLoggedInHomeSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    catalogs = serializers.ListField()
    next_api = serializers.DictField()
# ---------------------------------------------------


# ---{Home}------------------------------------------
class HomeNextAPIs(object):
    def __init__(self, reserves, logs, setting, reserve_and_history):
        self.reserves = reserves
        self.logs = logs
        self.setting = setting
        self.reserve_and_history = reserve_and_history


class HomeNextAPISerializer(serializers.Serializer):
    reserves = serializers.URLField()
    logs = serializers.URLField()
    setting = serializers.URLField()
    reserve_and_history = serializers.URLField()


class HomeSerializer(serializers.ModelSerializer):
    catalogs = serializers.SerializerMethodField()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'catalogs',
            'next_api',
        )

    def get_catalogs(self, instance):
        try:
            catalogs = stylist_models.CatalogImage.objects.all()
            pagenator = Paginator(catalogs, 10)
            page = self.context['request'].query_params.get('page') or 1
            catalog_contents = HomeCatalogsSerializer(
                pagenator.page(page),
                many=True,
                context={'request': self.context['request']}
            ).data
            return catalog_contents
        except django.core.paginator.EmptyPage:
            page = 1
            catalog_contents = HomeCatalogsSerializer(
                pagenator.page(page),
                many=True,
                context={'request': self.context['request']}
            ).data
            return catalog_contents

    def get_next_api(self, instance):
        try:
            next_api_urls = HomeNextAPISerializer(HomeNextAPIs(
                reserves=reverse(viewname='reserves-detail',
                                 request=self.context['request']),
                logs=reverse(viewname='logs-detail',
                             request=self.context['request']),
                setting=reverse(viewname='setting-detail',
                                request=self.context['request']),
                reserve_and_history=reverse(viewname='reserve_and_history-list',
                                            request=self.context['request']),
            )).data
            return next_api_urls
        except:
            next_api_urls = None
            return next_api_urls
# ---------------------------------------------------


# ---{Reserves}--------------------------------------
class ReservesStylistProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = stylist_models.StylistProfile
        fields = (
            'place',
            'phone_number',
        )


class ReservesMenuSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = stylist_models.Menu
        fields = (
            'menu_name',
            'price',
            'time',
        )


class ReservesNextAPIs(object):
    def __init__(self, home, logs, setting):
        self.home = home
        self.logs = logs
        self.setting = setting


class ReservesNextAPISerializer(serializers.Serializer):
    home = serializers.URLField()
    logs = serializers.URLField()
    setting = serializers.URLField()


class ReservesReserveAndHistorySerializer(serializers.HyperlinkedModelSerializer):
    api = serializers.HyperlinkedIdentityField(view_name='reserve_and_history-detail')
    stylist_name = serializers.SerializerMethodField()
    stylist_info = serializers.SerializerMethodField()
    menu_info = serializers.SerializerMethodField()
    time = DateTimeRangeField()

    class Meta:
        model = ReserveAndHistory
        fields = (
            'stylist_name',
            'stylist_info',
            'menu_info',
            'time',
            'api',
        )

    def get_stylist_name(self, instance):
        return instance.stylist.stylist.last_name + ' ' + instance.stylist.stylist.first_name

    def get_stylist_info(self, instance):
        try:
            stylist_info = ReservesStylistProfileSerializer(
                stylist_models.StylistProfile.objects.get(stylist=instance.stylist)
            ).data
            return stylist_info
        except:
            stylist_info = None
            return stylist_info

    def get_menu_info(self, instance):
        try:
            menu_info = ReservesMenuSerializer(
                stylist_models.Menu.objects.get(id=instance.menu.id)
            ).data
            return menu_info
        except:
            menu_info = None
            return menu_info


class ReservesSerializer(serializers.ModelSerializer):
    reserves = serializers.SerializerMethodField()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'reserves',
            'next_api',
        )

    def get_reserves(self, instance):
        try:

            reserve_contents = ReservesReserveAndHistorySerializer(
                ReserveAndHistory.objects.filter(
                    customer=instance,
                    time__endswith__gte=timezone.datetime.now(),
                ).all(),
                many=True,
                context={'request': self.context['request']}
            ).data
            return reserve_contents
        except:
            reserve_contents = None
            return reserve_contents

    def get_next_api(self, instance):
        try:
            next_api_urls = ReservesNextAPISerializer(ReservesNextAPIs(
                home=reverse(viewname='c_home-detail',
                             request=self.context['request']),
                logs=reverse(viewname='logs-detail',
                             request=self.context['request']),
                setting=reverse(viewname='setting-detail',
                                request=self.context['request']),
            )).data
            return next_api_urls
        except:
            next_api_urls = None
            return next_api_urls
# ---------------------------------------------------


# ---{Logs}------------------------------------------
class LogsStylistProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = stylist_models.StylistProfile
        fields = (
            'place',
            'phone_number',
        )


class LogsMenuSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = stylist_models.Menu
        fields = (
            'menu_name',
            'price',
        )


class LogsNextAPIs(object):
    def __init__(self, home, reserves, setting):
        self.home = home
        self.reserves = reserves
        self.setting = setting


class LogsNextAPISerializer(serializers.Serializer):
    home = serializers.URLField()
    reserves = serializers.URLField()
    setting = serializers.URLField()


class LogsReserveAndHistorySerializer(serializers.HyperlinkedModelSerializer):
    api = serializers.HyperlinkedIdentityField(view_name='reserve_and_history-detail')
    stylist_name = serializers.SerializerMethodField()
    stylist_info = serializers.SerializerMethodField()
    menu_info = serializers.SerializerMethodField()
    time = DateTimeRangeField()

    class Meta:
        model = ReserveAndHistory
        fields = (
            'stylist_name',
            'rating',
            'stylist_info',
            'menu_info',
            'time',
            'api',
        )

    def get_stylist_name(self, instance):
        return instance.stylist.stylist.last_name + ' ' + instance.stylist.stylist.first_name

    def get_stylist_info(self, instance):
        try:
            stylist_info = LogsStylistProfileSerializer(
                stylist_models.StylistProfile.objects.get(stylist=instance.stylist)
            ).data
            return stylist_info
        except:
            stylist_info = None
            return stylist_info

    def get_menu_info(self, instance):
        try:
            menu_info = LogsMenuSerializer(
                stylist_models.Menu.objects.get(id=instance.menu.id)
            ).data
            return menu_info
        except:
            menu_info = None
            return menu_info


class LogsSerializer(serializers.ModelSerializer):
    logs = serializers.SerializerMethodField()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'logs',
            'next_api',
        )

    def get_logs(self, instance):
        try:
            log_contents = LogsReserveAndHistorySerializer(
                ReserveAndHistory.objects.filter(
                    customer=instance,
                    time__endswith__lte=timezone.datetime.now(),
                ).all(),
                many=True,
                context={'request': self.context['request']}
            ).data
            return log_contents
        except:
            log_contents = None
            return log_contents

    def get_next_api(self, instance):
        try:
            next_api_urls = LogsNextAPISerializer(LogsNextAPIs(
                home=reverse(viewname='c_home-detail',
                             request=self.context['request']),
                reserves=reverse(viewname='reserves-detail',
                                 request=self.context['request']),
                setting=reverse(viewname='setting-detail',
                                request=self.context['request']),
            )).data
            return next_api_urls
        except:
            next_api_urls = None
            return next_api_urls
# ---------------------------------------------------


# ---{Setting}---------------------------------------
class SettingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'last_name',
            'first_name',
            'email',
        )


class SettingNextAPIs(object):
    def __init__(self, home, reserves, setting, users):
        self.home = home
        self.reserves = reserves
        self.setting = setting
        self.users = users


class SettingNextAPISerializer(serializers.Serializer):
    home = serializers.URLField()
    reserves = serializers.URLField()
    setting = serializers.URLField()
    users = serializers.URLField()


class SettingSerializer(serializers.ModelSerializer):
    customer = SettingUserSerializer()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'customer',
            'img',
            'age',
            'gender',
            'phone_number',
            'next_api',
        )

    def get_next_api(self, instance):
        try:
            next_api_urls = SettingNextAPISerializer(SettingNextAPIs(
                home=reverse(viewname='c_home-detail',
                             request=self.context['request']),
                reserves=reverse(viewname='reserves-detail',
                                 request=self.context['request']),
                setting=reverse(viewname='setting-detail',
                                request=self.context['request']),
                users=reverse(viewname='users-detail',
                              args=[instance.customer.id],
                              request=self.context['request']),
            )).data
            return next_api_urls
        except:
            next_api_urls = None
            return next_api_urls

    def update(self, instance, validated_data):
        """
        OVERRIDE:

        """
        if 'img' in validated_data.keys():
            old_img_path = os.path.join(MEDIA_ROOT, str(instance.img))
            if os.path.exists(old_img_path):
                os.remove(old_img_path)

        if 'customer' in validated_data.keys():
            user_info = validated_data.pop('customer')
            user_fields = instance.customer

            user_fields.last_name = user_info.get('last_name', user_fields.last_name)
            user_fields.first_name = user_info.get('first_name', user_fields.first_name)
            user_fields.email = user_info.get('email', user_fields.email)
            user_fields.save()

        instance.img = validated_data.get('img', instance.img)
        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.save()

        return instance
# ---------------------------------------------------
