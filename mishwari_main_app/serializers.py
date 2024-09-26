import random
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Driver,MainTrip,AllTrips,CityList,Seat,Booking,Bus,BusOperator,Passenger,BookingPassenger, TemporaryMobileVerification,Profile


class MobileVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemporaryMobileVerification
        fields = ["mobile_number", "otp_code", "is_verified"]

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username","email","first_name","last_name"]
        # fields = "__all__"

# class JwtUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['id','user','mobile_number', 'full_name','birth_date', 'gender', 'address']



class ProfileCompletionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    user = UserSerializer(read_only=True)
    # password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Profile
        fields = ['user','username', 'full_name', 'birth_date', 'gender']
        extra_kwargs = {
            'full_name':{'required': True}, 
            'username':{'required': True}
        }

    def create(self, validated_data):
        username = validated_data.pop('username', None)
        # password = validated_data.pop('password')
        mobile_number = self.context.get('mobile_number', None)

        if not username : 
            raise serializers.ValidationError({'message': 'Username is required for profile creation'})
        
        user = User.objects.create_user(username=username)
        

        profile = Profile.objects.create(user=user,mobile_number=mobile_number, **validated_data)
        
        return profile
    

    def update(self, instance, validated_data): 
        user = instance.user

        username = validated_data.get('username', user.username)
        print("validated data", username)
        # password = validated_data.get('password', None)

        user.username = username
        print("user", user.username)
        user.save()

        # profile
        instance.full_name = validated_data.get('full_name', instance.full_name)
        # instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.gender = validated_data.get('gender', instance.gender)
        # instance.address = validated_data.get('address', instance.address)
        instance.save()
        
        return instance





class BusOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusOperator
        fields = ["id", "name"]
class DriverSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True)
    operator = BusOperatorSerializer(read_only=True)
    class Meta:
        model= Driver 
        fields = ['id','d_name','driver_rating','operator']

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ["id", "bus_number","bus_type", "capacity","amenities"]

class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model= CityList
        fields = ["id","city"]


class TripsSerializer(serializers.ModelSerializer):
    # sub_trips = AllTripsSerializer(many=True, read_only=True)
    # driver_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Driver.objects.all(), 
    #     source='driver',  
    #     write_only=True  
    # )
    driver = DriverSerializer(read_only=True)

    bus = BusSerializer( read_only=True)

    class Meta:
        model= MainTrip 
        fields = ['id','driver','path_road','bus']



class AllTripsSerializer(serializers.ModelSerializer):
    pickup = CitiesSerializer(read_only=True)
    destination = CitiesSerializer(read_only=True)
    main_trip = TripsSerializer(read_only=True, source='trip')
    driver_id = serializers.PrimaryKeyRelatedField(
        queryset=Driver.objects.all(), 
        source='driver',  
        write_only=True  
    )
    # driver = DriverSerializer(read_only=True)

    class Meta:
        model= AllTrips 
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
    trip_type = serializers.CharField(max_length=16)

    def to_representation(self, instance):
        """
        Custom representation based on the instance type.
        """
        representation = super(CombinedTripSerializer, self).to_representation(instance)
        
        # Add or remove fields based on the model instance type
        if isinstance(instance, MainTrip):
            # Add or modify fields specific to Trips
            # For example, if Trips has a field not present in SubTrips
            # representation['specific_field'] = instance.specific_field
            pass
        elif isinstance(instance, AllTrips):
            # Add or modify fields specific to SubTrips
            # For example, if SubTrips has a field not present in Trips
            # representation['different_field'] = instance.different_field
            pass

        return representation
    


# Booking Serializers

class SeatSerializer(serializers.ModelSerializer):       
    trip_detail = serializers.CharField(source='trip.id', read_only=True)                          
    class Meta:
        model = Seat
        fields = ['id', 'seat_number', 'is_booked','trip_detail']


class BookingTripSerializer(serializers.ModelSerializer):
    # pickup = CitiesSerializer(read_only=True)
    seats = SeatSerializer(many=True, read_only=True)
    main_trip_id = serializers.SerializerMethodField()

    class Meta: 
        model = AllTrips
        fields = ['id', 'main_trip_id', 'pickup', 'destination', 'departure_time', 'arrival_time', 'seats']

    def get_main_trip_id(self, obj):
        return obj.trip.id


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'email', 'phone','age','is_checked','gender']

class BookingSerializer2(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    trip = serializers.PrimaryKeyRelatedField(queryset=AllTrips.objects.all()) # so i can perform create booking with only trip (id)

    passengers = PassengerSerializer(many=True)  # removed read_only=True to allow writing

    class Meta:
        model = Booking
        fields = ['id', 'user', 'trip', 'booking_time', 'payment_method','amount', 'status', 'is_paid', 'passengers']

    def validate(self, data):
        # print("validate data:", data)
        trip = data.get('trip')
        passengers = self.initial_data.get('passengers', [])  # Use initial_data to get the actual (input) data

        if trip:
            org_trip = AllTrips.objects.filter(id=trip.id)
            org_price = org_trip[0].price
            amount = data.get('amount')
            available_seats = Seat.objects.filter(trip=trip, is_booked=False).count() 
            print("available seats:", available_seats)
            if not available_seats :
                raise serializers.ValidationError(f"No seats available for trip {trip.id}: {available_seats}")
            if len(passengers) > available_seats:
                raise serializers.ValidationError(f"Too many passengers for available seats. Only {available_seats} seats are available in the selected trip.")
            
            # validate the correct amount 
            if amount != (org_price * len(passengers)) :
                raise serializers.ValidationError(f"Invalid amount for the selected trip. Expected {org_price * len(passengers)}, but received {amount}.")
            
        return data

    def create(self, validated_data):
        initial_passengers_data = self.initial_data.get('passengers', [])
        # print('initial_passengers_data: ', initial_passengers_data)
        user = self.context['request'].user  # Ensure this matches the user making the request

        # Ensure 'user' is not in validated_data
        validated_data.pop('user', None)

        # Remove passengers from validated_data
        validated_data.pop('passengers', [])

        # Create the booking instance without passengers
        booking = Booking.objects.create(**validated_data, user=user)
        self.assign_seats_and_passengers(booking, initial_passengers_data)

        return booking


    def assign_seats_and_passengers(self, booking, initial_passengers_data):
        # Retrieve available seats for the trip
        available_seats = list(Seat.objects.filter(trip=booking.trip, is_booked=False))
        random.shuffle(available_seats)  # Randomize the list of available seats
        print("available create seats: ", available_seats)

        # Collect passengers to add them later
        passengers_to_add = []

        # Assign each passenger a random seat
        for passenger_info in initial_passengers_data:
            passenger_id = passenger_info.get('id')
            # NOTE we get passenger id from initial_passengers_data cuz validated_data by default does pass the id
            if passenger_id is None:
                passenger = Passenger.objects.create(user=booking.user, **passenger_info)
            else:
                # Remove 'id' from the dictionary to avoid conflicts
                passenger_info.pop('id', None)
                passenger, _ = Passenger.objects.update_or_create(id=passenger_id, defaults={**passenger_info, 'user': user})

            if available_seats:
                selected_seat = available_seats.pop()
                selected_seat.is_booked = True
                selected_seat.save()
                BookingPassenger.objects.create(booking=booking, passenger=passenger, seat=selected_seat)
                passengers_to_add.append(passenger)
            else:
                raise serializers.ValidationError("Not enough seats available.")

        # Add passengers to the booking using the set method
        booking.passengers.set(passengers_to_add)

        
    
    # to_representation() is important to get all trip details when GET request and post booking using only trip.id
    def to_representation(self, instance): 
        representation = super().to_representation(instance)
        representation['trip'] = AllTripsSerializer(instance.trip).data
        return representation
    
    # LOOP validate passenger by id to ignore passenger if it already there
    # TODO: handle passenger updation
    #