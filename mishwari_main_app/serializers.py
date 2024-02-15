from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Driver,Trips,SubTrips,CityList


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

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model= CityList
        fields = ["id","city"]

class SubTripsSerializer(serializers.ModelSerializer):
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(), 
        source='driver',  
        write_only=True  
    )
    driver = DriverSerializer(read_only=True)

    class Meta:
        model= SubTrips 
        fields = "__all__"

class TripsSerializer(serializers.ModelSerializer):
    sub_trips = SubTripsSerializer(many=True, read_only=True)
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(), 
        source='driver',  
        write_only=True  
    )
    driver = DriverSerializer(read_only=True)

    class Meta:
        model= Trips 
        fields = "__all__"


class CombinedTripSerializer(serializers.Serializer):
    # Assuming these fields are common and exist in both Trips and SubTrips models
    id = serializers.IntegerField()
    driver = DriverSerializer(read_only=True)
    pickup = serializers.CharField(max_length=16)
    destination = serializers.CharField(max_length=16)
    path_road = serializers.CharField(max_length=32, required=False)
    price = serializers.IntegerField()
    driver_id = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all(), source='driver')
    created_at = serializers.DateTimeField()
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField(required=False)
    distance = serializers.FloatField()
    trip_status = serializers.CharField(max_length=16)
    available_seats = serializers.IntegerField(required=False)

    def to_representation(self, instance):
        """
        Custom representation based on the instance type.
        """
        representation = super(CombinedTripSerializer, self).to_representation(instance)
        
        # Add or remove fields based on the model instance type
        if isinstance(instance, Trips):
            # Add or modify fields specific to Trips
            # For example, if Trips has a field not present in SubTrips
            # representation['specific_field'] = instance.specific_field
            pass
        elif isinstance(instance, SubTrips):
            # Add or modify fields specific to SubTrips
            # For example, if SubTrips has a field not present in Trips
            # representation['different_field'] = instance.different_field
            pass

        return representation



