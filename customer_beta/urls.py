from rest_framework import routers
from django.urls import path, include
from .views import *


router = routers.DefaultRouter()
router.register(r'customer-profiles', CustomerProfileViewSet, 'customer_profiles')
router.register(r'reserve-and-histories', ReserveAndHistoryViewSet, 'reserve_and_history')
router.register(r'timeslots', TimeslotsViewSet, 'timeslots')


# ---{Home}------------------------------------------
c_home_list = HomeViewSet.as_view({'get': 'list',
                                   'post': 'create'})
c_home_detail = HomeViewSet.as_view({'get': 'retrieve',
                                     'post': 'update',
                                     'delete': 'destroy'})
# ---------------------------------------------------

# ---{Reserves}--------------------------------------
reserves_list = ReservesViewSet.as_view({'get': 'list',
                                         'post': 'create'})
reserves_detail = ReservesViewSet.as_view({'get': 'retrieve',
                                           'post': 'update',
                                           'delete': 'destroy'})
# ---------------------------------------------------

# ---{Logs}------------------------------------------
logs_list = LogsViewSet.as_view({'get': 'list',
                                 'post': 'create'})
logs_detail = LogsViewSet.as_view({'get': 'retrieve',
                                   'post': 'update',
                                   'delete': 'destroy'})
# ---------------------------------------------------

# ---{Setting}---------------------------------------
setting_list = SettingViewSet.as_view({'get': 'list',
                                       'post': 'create'})
setting_detail = SettingViewSet.as_view({'get': 'retrieve',
                                         'put': 'update',
                                         'patch': 'partial_update',
                                         'delete': 'destroy'})
# ---------------------------------------------------


urlpatterns = [
    path(r'', include(router.urls)),
    path(r'home/', NoLoggedInHomeView.as_view(), name='no_logged_in_c_home'),
    path(r'home/me/', c_home_detail, name='c_home-detail'),
    path(r'reserve/me/', reserves_detail, name='reserves-detail'),
    path(r'log/me/', logs_detail, name='logs-detail'),
    path(r'setting/me/', setting_detail, name='setting-detail'),
]
