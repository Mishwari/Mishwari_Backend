from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Driver,Trips


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id",  "is_superuser", "username","email","first_name","last_name","is_staff"]
        # fields = "__all__"

# class JwtUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User

class DriverSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    class Meta:
        model= Driver 
        fields = "__all__"


class TripsSerializer(serializers.ModelSerializer):
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(), 
        source='driver',  
        write_only=True  
    )
    driver = DriverSerializer(read_only=True)

    class Meta:
        model= Trips 
        fields = "__all__"

