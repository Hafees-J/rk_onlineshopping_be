from django.db import models
from user.models import User


class Shop(models.Model):
    SHOP_TYPES = (
        ('restaurant', 'Restaurant'),
        ('supermarket', 'Supermarket'),
        ('allmart', 'Allmart'),
    )
    name = models.CharField(max_length=255)
    shop_type = models.CharField(max_length=50, choices=SHOP_TYPES, default='restaurant')

    def __str__(self):
        return self.name


class Branch(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="branches")
    gst_number = models.CharField(max_length=15, unique=True)
    contact_number = models.CharField(max_length=15)
    address = models.TextField()
    location = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='shop_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.shop.name} - {self.name}"

class DeliveryCondition(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="delivery_conditions")
    free_delivery_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    free_delivery_distance = models.DecimalField(max_digits=10, decimal_places=2, default=5)
    maximum_distance = models.DecimalField(max_digits=6, decimal_places=2, default=10)  # in km
    per_km_charge = models.DecimalField(max_digits=10, decimal_places=2, default=10)

    def __str__(self):
        return f"{self.branch.name} Delivery Conditions"
