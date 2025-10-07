from django.contrib import admin
from .models import CustomerProfile, User, Address

admin.site.register(User)
admin.site.register(CustomerProfile)
admin.site.register(Address)