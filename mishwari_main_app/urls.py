from django.urls import path,include
from rest_framework import routers

from django.contrib.auth.models import User

from .views import (
    TripsViewSet,DriverView,AllTripsView,JwtUserView,
    DriverTripView,JwtDriverView,RouteViewSet,
    TestGetView,CitiesView,BookingViewSet,BookingTripsViewSet,PassengersViewSet,
    stripe_webhook
    )
    

from .allviews.authView import (MobileLoginView, 
                                whatsapp_webhook,
                                # ProfileView
                                )

router = routers.DefaultRouter()
# router.register(r"users", UserViewSet)
router.register(r"drivers", DriverView)
router.register(r"trips", AllTripsView, basename='trips') # client - trips list (from - to)

router.register(r"user",JwtUserView, basename="jwt-user")
router.register(r"driver-details",JwtDriverView, basename="driver-details")
router.register(r"driver-trips",DriverTripView, basename="driver-trips")

router.register(r"route",RouteViewSet,basename="route")

router.register(r"test-create", TripsViewSet,basename="test-create")
router.register(r"test-get", TestGetView,basename="test-get")
router.register(r"city-list",CitiesView,basename="city-list")
router.register(r"booking",BookingViewSet,basename="booking")
router.register(r"seats",BookingTripsViewSet,basename="seats")
router.register(r"passengers",PassengersViewSet, basename="user-passengers")
router.register(r"mobile-login",MobileLoginView, basename="mobile-login")
# router.register(r"profile",ProfileView,basename="profile")




urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),    # to login in rest_framework
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
    path('whatsapp-response/', whatsapp_webhook.as_view(), name='whatsapp-response'),

]

