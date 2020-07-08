from .models import *
from rest_framework import serializers
from customer_beta import models as customer_models
from rest_framework.reverse import reverse
from datetime import datetime
from django.db.models import Avg
from django.contrib.auth import authenticate, password_validation
from django.core.paginator import Paginator
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
import os
from monsiApiRehearsalBetaV2.settings import MEDIA_ROOT


# ---{General serializers for REST}------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'last_name',
            'first_name',
            'email',
        )
        read_only_fields = (
            'id',
            'username'
        )
        write_only_fields = ('password',)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        else:
            instance = super().update(instance, validated_data)
        instance.save()
        return instance


class StylistProfileSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        model = StylistProfile
        fields = (
            'id',
            'img',
            'phone_number',
            'year',
            'salon_name',
            'place',
            'access',
        )
        read_only_fields = ('id',)

    def get_id(self, instance):
        return instance.stylist.id


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = (
            'id',
            'problem',
        )
        read_only_fields = ('id',)


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = (
            'id',
            'menu_name',
            'price',
            'time',
            'problem',
        )
        read_only_fields = ('id',)


class CatalogImageSerializer(serializers.ModelSerializer):
    menu_name = serializers.SerializerMethodField()

    class Meta:
        model = CatalogImage
        fields = (
            'id',
            'before_img',
            'after_img',
            'menu',
            'menu_name',
            'age',
            'gender',
        )
        read_only_fields = (
            'id',
            'menu_name',
        )
        extra_kwargs = {
            'menu': {'write_only': True},
        }

    def get_menu_name(self, instance):
        return instance.menu.menu_name

    def update(self, instance, validated_data):
        """
        OVERRIDE:
        """
        if 'before_img' in validated_data.keys():
            old_img_path = os.path.join(MEDIA_ROOT, str(instance.before_img))
            if os.path.exists(old_img_path):
                os.remove(old_img_path)
        if 'after_img' in validated_data.keys():
            old_img_path = os.path.join(MEDIA_ROOT, str(instance.after_img))
            if os.path.exists(old_img_path):
                os.remove(old_img_path)

        instance.before_img = validated_data.get('before_img', instance.before_img)
        instance.after_img = validated_data.get('after_img', instance.after_img)
        instance.menu = validated_data.get('menu', instance.menu)
        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()

        return instance
# ---------------------------------------------------


# ---{For Home}--------------------------------------
class HomeUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'last_name',
            'first_name',
        )


class HomeMenuSerializer(serializers.HyperlinkedModelSerializer):
    api = serializers.HyperlinkedIdentityField(view_name='menus-detail')

    class Meta:
        model = Menu
        fields = (
            'menu_name',
            'img',
            'price',
            'time',
            'api',
        )


class HomeNextAPIs(object):
    def __init__(self, edit_catalogs, schedule, menus, users):
        self.edit_catalogs = edit_catalogs
        self.schedule = schedule
        self.menus = menus
        self.users = users


class HomeNextAPISerializer(serializers.Serializer):
    edit_catalogs = serializers.URLField()
    schedule = serializers.URLField()
    menus = serializers.URLField()
    users = serializers.URLField()


class HomeSerializer(serializers.ModelSerializer):
    stylist = HomeUserSerializer()
    menus = serializers.SerializerMethodField()
    rating_average = serializers.SerializerMethodField()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = StylistProfile
        fields = (
            'stylist',
            'img',
            'year',
            'phone_number',
            'salon_name',
            'salon_img',
            'place',
            'access',
            'rating_average',
            'menus',
            'next_api',
        )
        read_only_fields = (
            'full_name',
            'rating_average',
            'menus',
            'next_api',
        )

    def get_menus(self, instance):
        try:
            menus_contents = HomeMenuSerializer(
                Menu.objects.filter(stylist=instance).all(),
                many=True,
                context={'request': self.context['request']}
            ).data
            return menus_contents
        except:
            menus_contents = None
            return menus_contents

    def get_rating_average(self, instance):
        try:
            menus = Menu.objects.filter(stylist=instance).all()
            rating_average = customer_models.ReserveAndHistory.objects.filter(
                menu__in=menus,
                timeslot__time__lt=datetime.now()
            ).all().aggregate(Avg('rating'))
            return rating_average['rating__avg']
        except:
            rating_average = None
            return rating_average

    def get_next_api(self, instance):
        next_api_urls = HomeNextAPISerializer(HomeNextAPIs(
            edit_catalogs=reverse(viewname='edit_catalogs-detail',
                                  request=self.context['request']),
            schedule=reverse(viewname='schedule-detail',
                             request=self.context['request']),
            menus=reverse(viewname='menus-list',
                          request=self.context['request']),
            users=reverse(viewname='users-detail',
                          args=[instance.stylist.id],
                          request=self.context['request']),
        )).data
        return next_api_urls

    def update(self, instance, validated_data):
        """
        OVERRIDE:
        """
        if 'img' in validated_data.keys():
            old_img_path = os.path.join(MEDIA_ROOT, str(instance.img))
            if os.path.exists(old_img_path):
                os.remove(old_img_path)
        if 'salon_img' in validated_data.keys():
            old_img_path = os.path.join(MEDIA_ROOT, str(instance.salon_img))
            if os.path.exists(old_img_path):
                os.remove(old_img_path)

        if 'stylist' in validated_data.keys():
            user_info = validated_data.pop('stylist')
            user_fields = instance.stylist

            user_fields.last_name = user_info.get('last_name', user_fields.last_name)
            user_fields.first_name = user_info.get('first_name', user_fields.first_name)
            user_fields.save()

        instance.img = validated_data.get('img', instance.img)
        instance.year = validated_data.get('year', instance.year)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.salon_name = validated_data.get('salon_name', instance.salon_name)
        instance.salon_img = validated_data.get('salon_img', instance.salon_img)
        instance.place = validated_data.get('place', instance.place)
        instance.access = validated_data.get('access', instance.access)
        instance.save()

        return instance
# ---------------------------------------------------


# ---{For Edit-Catalogs}-----------------------------
class ECCatalogSerializer(serializers.HyperlinkedModelSerializer):
    api = serializers.HyperlinkedIdentityField(view_name='catalog_images-detail')
    menu_name = serializers.SerializerMethodField()

    class Meta:
        model = CatalogImage
        fields = (
            'before_img',
            'after_img',
            'menu_name',
            'age',
            'gender',
            'api',
        )

    def get_menu_name(self, instance):
        return instance.menu.menu_name


class EditCatalogsNextAPIs(object):
    def __init__(self, home, schedule, catalogs):
        self.home = home
        self.schedule = schedule
        self.catalogs = catalogs


class EditCatalogsNextAPISerializer(serializers.Serializer):
    home = serializers.URLField()
    schedule = serializers.URLField()
    catalogs = serializers.URLField()


class EditCatalogsSerializer(serializers.ModelSerializer):
    catalogs = serializers.SerializerMethodField()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = StylistProfile
        fields = (
            'catalogs',
            'next_api',
        )

    def get_catalogs(self, instance):
        try:
            menu_instances = Menu.objects.filter(stylist=instance).all()
            catalog_contents = ECCatalogSerializer(
                CatalogImage.objects.filter(menu__in=menu_instances).all(),
                many=True,
                context={'request': self.context['request']}
            ).data
            return catalog_contents
        except:
            catalog_contents = None
            return catalog_contents

    def get_next_api(self, instance):
        try:
            next_api_urls = EditCatalogsNextAPISerializer(EditCatalogsNextAPIs(
                home=reverse(viewname='home-detail',
                             request=self.context['request']),
                schedule=reverse(viewname='schedule-detail',
                                 request=self.context['request']),
                catalogs=reverse(viewname='catalog_images-list',
                                 request=self.context['request']),
            )).data
            return next_api_urls
        except:
            next_api_urls = None
            return next_api_urls
# ---------------------------------------------------


# ---{For Schedule}----------------------------------
class ScheduleReserveSerializer(serializers.HyperlinkedModelSerializer):
    customer_name = serializers.SerializerMethodField()
    menu_name = serializers.SerializerMethodField()
    timeslot = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    place = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = customer_models.ReserveAndHistory
        fields = (
            'customer_name',
            'menu_name',
            'timeslot',
            'price',
            'place',
            'phone_number',
        )

    def get_customer_name(self, instance):
        return instance.customer.customer.last_name + ' ' + instance.customer.customer.first_name

    def get_menu_name(self, instance):
        return instance.menu.menu_name

    def get_timeslot(self, instance):
        return instance.timeslot.time

    def get_price(self, instance):
        return instance.menu.price

    def get_place(self, instance):
        return instance.menu.stylist.place

    def get_phone_number(self, instance):
        return instance.menu.stylist.phone_number


class ScheduleNextAPIs(object):
    def __init__(self, home, edit_catalogs, timeslots, catalogs):
        self.home = home
        self.edit_catalogs = edit_catalogs
        self.timeslots = timeslots
        self.catalogs = catalogs


class ScheduleNextAPISerializer(serializers.Serializer):
    home = serializers.URLField()
    edit_catalogs = serializers.URLField()
    timeslots = serializers.URLField()
    catalogs = serializers.URLField()


class ScheduleSerializer(serializers.ModelSerializer):
    reserves = serializers.SerializerMethodField()
    next_api = serializers.SerializerMethodField()

    class Meta:
        model = StylistProfile
        fields = (
            'reserves',
            'next_api',
        )

    def get_reserves(self, instance):
        try:
            if self.context['request'].query_params.get('year') and self.context['request'].query_params.get('month') \
                    and self.context['request'].query_params.get('day'):
                year_param = self.context['request'].query_params.get('year')
                month_param = self.context['request'].query_params.get('month')
                day_param = self.context['request'].query_params.get('day')
            else:
                today_datetime = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
                year_param = today_datetime[:4]
                month_param = today_datetime[5:7]
                day_param = today_datetime[8:10]

            menu_instances = Menu.objects.filter(stylist=instance).all()
            timeslot_instances = customer_models.Timeslots.objects.filter(time__year=year_param,
                                                                          time__month=month_param,
                                                                          time__day=day_param).all()
            reserve_contents = ScheduleReserveSerializer(
                customer_models.ReserveAndHistory.objects.filter(menu__in=menu_instances,
                                                                 timeslot__in=timeslot_instances).all(),
                many=True,
                context={'request': self.context['request']}
            ).data
            return reserve_contents
        except:
            reserve_contents = None
            return reserve_contents

    def get_next_api(self, instance):
        try:
            next_api_urls = ScheduleNextAPISerializer(ScheduleNextAPIs(
                home=reverse(viewname='home-detail',
                             request=self.context['request']),
                edit_catalogs=reverse(viewname='edit_catalogs-detail',
                                      request=self.context['request']),
                timeslots=reverse(viewname='timeslots-list',
                                  request=self.context['request']),
                catalogs=reverse(viewname='catalog_images-list',
                                 request=self.context['request']),
            )).data
            return next_api_urls
        except:
            next_api_urls = None
            return next_api_urls
# ---------------------------------------------------


# ---{FOR Register}------------------------------------
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        )
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            last_name=validated_data['last_name'],
            first_name=validated_data['first_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
# --------------------------------------------------------

