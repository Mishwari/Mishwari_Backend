from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Driver,MainTrip,CityList,AllTrips,Booking,Seat,Bus,BusOperator,Passenger,BookingPassenger,TemporaryMobileVerification,Profile

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):

    list_display = ["id","d_name" ]

    # def username(self, obj):
    #     return obj.user.username
    # username.admin_order_field = 'user__username'  # Allows column order sorting
    # username.short_description = 'Username'  # Renames column head


admin.site.register(MainTrip)
admin.site.register(AllTrips)

admin.site.register(CityList)

# admin.site.register(Booking)


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

    def clean_seats(self):
        seats = self.cleaned_data.get('seats')
        trip = self.cleaned_data.get('trip')

        if not trip:
            raise ValidationError("You must select a trip before choosing seats.")

        for seat in seats:
            if seat.trip is None:
                # Handle the case where a seat does not have an associated trip
                raise ValidationError(f"Seat {seat.seat_number} is not associated with any trip.")
            if seat.trip != trip:
                raise ValidationError("All selected seats must belong to the selected trip.")

        return seats
    

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = ['user', 'trip', 'booking_time', 'is_paid','status']

    # def save_model(self, request, obj, form, change):
    #     if form.is_valid():
    #         obj.save()

admin.site.register(Seat)

admin.site.register(Bus)

admin.site.register(BusOperator)

admin.site.register(Passenger)

admin.site.register(BookingPassenger)

admin.site.register(TemporaryMobileVerification)

admin.site.register(Profile)

