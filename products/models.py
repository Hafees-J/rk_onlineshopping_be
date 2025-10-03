from django.db import models
from shop.models import Shop


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='subcategory_images/', blank=True, null=True)

    class Meta:
        unique_together = ('category', 'name')  # prevent duplicates within category

    def __str__(self):
        return f"{self.name} ({self.category.name})"
    

class HSN(models.Model):
    hsncode = models.CharField(max_length=20, unique=True)
    cgst = models.DecimalField(max_digits=5, decimal_places=2)
    sgst = models.DecimalField(max_digits=5, decimal_places=2)
    igst = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.hsncode


class Item(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    hsn = models.ForeignKey(HSN, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")

    class Meta:
        unique_together = ('subcategory', 'name')  # prevent duplicates

    def __str__(self):
        return f"{self.name} - {self.subcategory.name}"



class ShopCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class ShopSubCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)

class ShopItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="shopitems")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="shopitems")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.PositiveIntegerField(default=0)
    available_from = models.TimeField(null=True, blank=True)
    available_till = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        unique_together = ('shop', 'item')  # same item shouldn’t repeat in same shop

    def __str__(self):
        return f"{self.item.name} @ {self.shop.name}"


class ShopItemOffer(models.Model):
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name="offers")
    offer_starting_datetime = models.DateTimeField()
    offer_ending_datetime = models.DateTimeField()
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Offer for {self.shop_item.item.name} in {self.shop_item.shop.name}"
