from django.db import models
from django.contrib.auth.models import User

car_type_choices = [
    ("جماعي","جماعي"),
    ("بلكة","بلكة")
]

city_choices = [
    
    ("سيئون","سيئون"),
    ("المكلا","المكلا"),
    ("عدن","عدن"),
    ("عتق","عتق"),
    ("تريم","تريم"),
    ("تعز","تعز"),
    ("صنعاء","صنعاء"),
    ("القطن","القطن"),
    ("شحن","شحن"),
    ("الوديعة","الوديعة"),
    ("مأرب","مأرب"),
    ("الحديدة","الحديدة"),
    ("إب","إب"),
    ("البيضاء","البيضاء"),
    ("جعار","جعار"),
    ("رضوم","رضوم"),
    ("يريم","يريم"),
    ("ذمار","ذمار")
]

class Driver(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips') #username, pass and email
    d_name = models.CharField(max_length=200)
    car_number = models.CharField(max_length=10)
    car_type = models.CharField(max_length=30, choices=car_type_choices, default="bulka")
    mobile_number = models.IntegerField()
    photo = models.ImageField(null=True, blank=True)
    car_photo = models.ImageField(null=True, blank=True)
    driver_rating = models.DecimalField(max_digits=5, decimal_places=2)
    national_id = models.CharField(max_length=20, null=True, blank=True)
    driver_license = models.CharField(max_length=16, null=True, blank=True)
    is_ac= models.BooleanField(default=False)
    is_wifi = models.BooleanField(default=False)
    is_charger = models.BooleanField(default=False)
    
    
    def __str__(self):
        return f"{self.user.username} ({self.d_name})"



class Trips(models.Model):
    pickup =models.CharField(max_length=16,null=False,blank=False,choices=city_choices)
    destination =models.CharField(max_length=16,null=False,blank=False,choices=city_choices)
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
    


class SubTrips(models.Model):
    trip = models.ForeignKey(Trips, null=False, on_delete=models.CASCADE, related_name='sub_trips')
    pickup =models.CharField(max_length=16,null=False,blank=False,choices=city_choices)
    destination =models.CharField(max_length=16,null=False,blank=False,choices=city_choices)
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
        return f"الرحلة ({self.trip.id}): {self.pickup} / {self.destination}  "

class CityList(models.Model):
    city = models.CharField(max_length=16,null=False,blank=False,unique=True,choices=city_choices)
    latitude = models.DecimalField(max_digits=10,decimal_places=6)
    longitude = models.DecimalField(max_digits=10,decimal_places=6)
    proximity = models.FloatField(default=1.0, help_text="Proximity from the nearest point of the poly line")

    class Meta: 
        constraints = [
            models.UniqueConstraint(fields=['latitude', 'longitude'], name='Unique Coordinates')
        ]

    def __str__(self):
        return f"{self.city} coords: {self.latitude}, {self.longitude}"
    

    @property
    def coordinates(self):
        return f"{self.latitude}, {self.longitude}"
    