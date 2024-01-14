from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny,IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication


from .serializers import UserSerializer,DriverSerializer,TripsSerializer
from  .models import Driver,Trips

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    def get_permissions(self):
        if self.request.method in ['GET']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
class JwtUserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # This line gets the user ID from the JWT token and returns the corresponding user
        return User.objects.filter(id=self.request.user.id)


class DriverView(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    
    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        return [IsAdminUser()]

class JwtDriverView(viewsets.ModelViewSet):
    serializer_class = DriverSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # This line gets the user ID from the JWT token and returns the corresponding user
        return Driver.objects.filter(user=self.request.user.id)



class TripsView(viewsets.ModelViewSet):
    serializer_class = TripsSerializer

    def get_queryset(self):
        # queryset = Trips.objects.all()
        pickup = self.request.query_params.get('pickup', None)
        destination = self.request.query_params.get('destination', None)

        if pickup and destination:
            queryset = Trips.objects.filter(pickup=pickup, destination=destination,trip_status=('pending' or 'active'))
            return queryset
        else:
            queryset = []
            return queryset
        
    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        return [IsAdminUser()]
    
class DriverTripView(viewsets.ModelViewSet):

    serializer_class = TripsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # This line gets the user ID from the JWT token and returns the corresponding user
        return Trips.objects.filter(driver__user=self.request.user.id)