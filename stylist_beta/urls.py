from rest_framework import routers
from django.urls import path, include
from .views import *


router = routers.DefaultRouter()
router.register(r'users', UserViewSet, 'users')
router.register(r'stylist-profiles', StylistProfileViewSet, 'stylist_profiles')
router.register(r'problems', ProblemViewSet, 'problems')
router.register(r'menus', MenuViewSet, 'menus')
router.register(r'catalog-images', CatalogImageViewSet, 'catalog_images')
router.register(r'register', RegisterViewSet, 'register')


# ---{Home}------------------------------------------
home_list = HomeViewSet.as_view({'get': 'list',
                                 'post': 'create'})
home_detail = HomeViewSet.as_view({'get': 'retrieve',
                                   'put': 'update',
                                   'patch': 'partial_update'})
# ---------------------------------------------------

# ---{Edit-Catalogs}---------------------------------
edit_catalogs_list = EditCatalogsViewSet.as_view({'get': 'list',
                                                  'post': 'create'})
edit_catalogs_detail = EditCatalogsViewSet.as_view({'get': 'retrieve'})
# ---------------------------------------------------

# ---{Schedule}--------------------------------------
schedule_list = ScheduleViewSet.as_view({'get': 'list',
                                         'post': 'create'})
schedule_detail = ScheduleViewSet.as_view({'get': 'retrieve'})
# ---------------------------------------------------

# ---{Register}--------------------------------------
register_list = RegisterViewSet.as_view({'post': 'create'})
# ---------------------------------------------------

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'auth-token/', CustomAuthToken.as_view()),
    path(r'register/', register_list, name='register'),
    path(r'home/me/', home_detail, name='home-detail'),
    path(r'edit-catalogs/me/', edit_catalogs_detail, name='edit_catalogs-detail'),
    path(r'schedule/me/', schedule_detail, name='schedule-detail'),
]