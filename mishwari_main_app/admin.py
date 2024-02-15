from django.contrib import admin
from .models import Driver,Trips,CityList,SubTrips
@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):

    list_display = ["id","username","d_name","car_type" ]

    def username(self, obj):
        return obj.user.username
    # username.admin_order_field = 'user__username'  # Allows column order sorting
    # username.short_description = 'Username'  # Renames column head


admin.site.register(Trips)
admin.site.register(SubTrips)

admin.site.register(CityList)

