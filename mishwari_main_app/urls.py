from django.urls import path,include
from rest_framework import routers

from django.contrib.auth.models import User
from .views import TripsViewSet, UserViewSet,DriverView,TripsView,JwtUserView,DriverTripView,JwtDriverView,RouteViewSet,TestGetView,CitiesView

router = routers.DefaultRouter()
# router.register(r"users", UserViewSet)
router.register(r"drivers", DriverView)
router.register(r"trips", TripsView, basename='trips') # client - trips list (from - to)

router.register(r"user",JwtUserView, basename="jwt-user")
router.register(r"driver-details",JwtDriverView, basename="driver-details")
router.register(r"driver-trips",DriverTripView, basename="driver-trips")

router.register(r"route",RouteViewSet,basename="route")

router.register(r"test-create", TripsViewSet,basename="test-create")
router.register(r"test-get", TestGetView,basename="test-get")
router.register(r"city-list",CitiesView,basename="city-list")




urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))    #to login in rest_framework

]

