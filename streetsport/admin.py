from django.contrib import admin
from .models import User, Stadium, Booking, Payment

admin.site.register(User)
admin.site.register(Stadium)
admin.site.register(Booking)
admin.site.register(Payment)
