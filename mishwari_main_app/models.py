from django.db import models
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from django.contrib.auth.models import User



class TemporaryMobileVerification(models.Model):
    mobile_number = models.CharField(max_length=15, unique=True)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    otp_sent_at = models.DateTimeField(auto_now_add=True)

    def otp_is_valid(self):
        expiry_time = self.otp_sent_at + timezone.timedelta(minutes=10)
        return timezone.now() < expiry_time
    
    def __str__(self):
        return f"{self.mobile_number} - {self.otp_code}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # email = models.EmailField(unique=False, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, unique=True, db_index=True)
    full_name = models.CharField(max_length=100,null=True, blank=True)
    address = models.CharField(max_length=150,null=True, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username




class CityList(models.Model):
    city = models.CharField(max_length=16,null=False,blank=False, unique=True)
    latitude = models.DecimalField(max_digits=10,decimal_places=6)
    longitude = models.DecimalField(max_digits=10,decimal_places=6)
    proximity = models.FloatField(default=1.0, help_text="Proximity from the nearest point of the poly line")

    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=['latitude', 'longitude'], name='Unique Coordinates')
        ]

    def __str__(self):
        return f"({self.id}){self.city} coords: {self.latitude}, {self.longitude}"
    

    @property
    def coordinates(self):
        return f"{self.latitude}, {self.longitude}"
    

    # booking 

class BusOperator(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.CharField(max_length=100)
    uses_own_system = models.BooleanField(default=False)

    api_url = models.URLField(max_length=200, blank=True, null=True)
    api_key = models.CharField(max_length=200, blank=True, null=True)

    operational_regions = models.ManyToManyField('CityList')

    def __str__(self):
        return f"{self.name} {'external' if self.uses_own_system else 'local'}"
    
class Bus(models.Model):
    operator = models.ForeignKey(BusOperator, on_delete=models.CASCADE, related_name="buses")
    bus_number = models.CharField(max_length=10, null=False, blank=False, unique=True)
    bus_type = models.CharField(max_length=30, null=False, blank=False)
    capacity = models.IntegerField()
    amenities = models.JSONField(default=dict)  # Stores amenities as key-value pairs, such as AC, Wi-Fi, etc.

    def __str__(self):
        return f"{self.bus_number} - {self.bus_type}"

class Driver(models.Model):
    buses = models.ManyToManyField(Bus, related_name='drivers')
    operator = models.ForeignKey(BusOperator, on_delete=models.CASCADE )
    
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips') #username, pass and email
    d_name = models.CharField(max_length=200)
    # car_number = models.CharField(max_length=10)
    # car_type = models.CharField(max_length=30, choices=car_type_choices, default="bulka")
    mobile_number = models.CharField(max_length=16)
    photo = models.ImageField(null=True, blank=True)
    # car_photo = models.ImageField(null=True, blank=True)
    driver_rating = models.DecimalField(max_digits=5, decimal_places=2)
    national_id = models.CharField(max_length=20, null=True, blank=True)
    driver_license = models.CharField(max_length=16, null=True, blank=True)
    # is_ac= models.BooleanField(default=False)
    # is_wifi = models.BooleanField(default=False)
    # is_charger = models.BooleanField(default=False)
    

    def __str__(self):
        return f" ({self.d_name})"
    


class MainTrip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.SET_NULL, null=True)
    pickup =models.ForeignKey(CityList, on_delete=models.PROTECT, related_name='trip_pickups')
    destination =models.ForeignKey(CityList, on_delete=models.PROTECT, related_name='trip_destinations')
    path_road = models.CharField(max_length=32,null=True, blank=True, default="مسار غير معروف")
    price = models.IntegerField(default=0)
    driver = models.ForeignKey(Driver,null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True) 
    departure_time = models.DateTimeField(null=False,blank=False)
    arrival_time = models.DateTimeField(null=True, blank=True)
    distance = models.FloatField(help_text="Distance in kilometers",default=0.0)
    trip_status = models.CharField(max_length=16, default="pending")
    available_seats = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.pickup}/{self.destination} - {self.created_at}"
    
    def trip_type(self):
        return 'main'
    


class AllTrips(models.Model):
    trip = models.ForeignKey(MainTrip, null=False, on_delete=models.CASCADE, related_name='sub_trips')
    pickup =models.ForeignKey(CityList, on_delete=models.PROTECT, related_name='subtrip_pickups')
    destination =models.ForeignKey(CityList, on_delete=models.PROTECT, related_name='subtrip_destinations')
    path_road = models.CharField(max_length=32,null=True, blank=True, default="مسار غير معروف") # to be removed
    price = models.IntegerField(default=0)
    driver = models.ForeignKey(Driver,null=True, on_delete=models.SET_NULL) # to be removed
    created_at = models.DateTimeField(auto_now_add=True) 
    departure_time = models.DateTimeField(null=False,blank=False)
    arrival_time = models.DateTimeField(null=True, blank=True)
    distance = models.FloatField(help_text="Distance in kilometers",default=0.0)
    trip_status = models.CharField(max_length=16, default="pending")
    available_seats = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"الرحلة ({self.trip.id}): {self.pickup} / {self.destination}"
    
    def trip_type(self):
        return'all'


class Seat(models.Model):
    trip = models.ForeignKey(AllTrips, on_delete=models.CASCADE, related_name="seats") # main
    seat_number = models.CharField(max_length=3, null=False, blank=False)
    is_booked = models.BooleanField(default=False)

    def __str__(self):


        return f" {self.seat_number} is - {"Booked" if self.is_booked else "Available"}"
    
# class Booking(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     trip = models.ForeignKey(AllTrips, on_delete=models.CASCADE)
#     seats = models.ManyToManyField(Seat)
#     booking_time = models.DateTimeField(auto_now_add=True)
#     is_paid = models.BooleanField(default=False)

#     def __str__(self):
#         username = self.user.username if self.user else "Unknown User"
#         booking_date = self.booking_time.strftime('%Y-%m-%d') if self.booking_time else "Pending"
#         return f"Booking By {username} on {booking_date}"

#     def save(self, *args, **kwargs):
#         # Using transaction.atomic ensures that all parts of the transaction are successfully completed
#         with transaction.atomic():
#             super(Booking, self).save(*args, **kwargs)
#             self.full_clean()

# # Receiver function to validate the many-to-many seats relationship after being saved
# @receiver(m2m_changed, sender=Booking.seats.through)
# def validate_seats(sender, instance, action, **kwargs):
#     if action == 'post_add':
#         if any(seat.trip != instance.trip for seat in instance.seats.all()):
#             raise ValidationError("All seats must belong to the selected trip.")
#     # Issue: should only the seats of the specific trip available to selects and save 



# Passenger management
genderChoices = [(
        'male', 'male'),
        ('female', 'female') ]
       

class Passenger(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    is_checked = models.BooleanField(default=False)
    gender = models.CharField(default=None, choices = genderChoices)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')

    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('wallet', 'Wallet'),
        ('stripe', 'Stripe'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(AllTrips, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)
    passengers = models.ManyToManyField(Passenger, through='BookingPassenger')
    is_paid = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    amount = models.IntegerField(default=0, null=True)



    def __str__(self):
        return f"Booking by {self.user.username} on {self.booking_time.strftime('%Y-%m-%d')} - {self.status}"
    
class BookingPassenger(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.passenger.name} - Seat {self.seat.seat_number if self.seat else 'N/A'}"
    

