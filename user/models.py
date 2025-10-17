from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('superadmin', 'Super Admin'),
        ('shopadmin', 'Shop Admin'),
        ('customer', 'Customer'),
        ('deliveryboy', 'Delivery Boy'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    mobile_number = models.CharField(max_length=15, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
    
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile of {self.user.username}"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)