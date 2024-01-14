from django.urls import path,include
from rest_framework import routers

from django.contrib.auth.models import User
from .views import UserViewSet,DriverView,TripsView,JwtUserView,DriverTripView,JwtDriverView

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"drivers", DriverView)
router.register(r"trips", TripsView, basename='trips')
router.register(r"user",JwtUserView, basename="jwt-user")
router.register(r"driver-trips",DriverTripView, basename="driver-trips")
router.register(r"driver-details",JwtDriverView, basename="driver-details")



urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls'))    #to login in rest_framework

]

