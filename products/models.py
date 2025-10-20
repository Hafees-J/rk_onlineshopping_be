from django.db import models
from shop.models import Shop
from decimal import Decimal, ROUND_HALF_UP


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
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class HSN(models.Model):
    hsncode = models.CharField(max_length=20, unique=True)
    gst = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.hsncode


class Item(models.Model):
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="items")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    hsn = models.ForeignKey(HSN, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")

    class Meta:
        unique_together = ('subcategory', 'name')

    def __str__(self):
        return f"{self.name} - {self.subcategory.name}"


# ✅ Added image + fallback
class ShopCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shopcategory_images/', blank=True, null=True)

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.category.image.url if self.category.image else None

    def __str__(self):
        return f"{self.category.name} ({self.shop.name})"


# ✅ Added image + fallback
class ShopSubCategory(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shopsubcategory_images/', blank=True, null=True)

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.subcategory.image.url if self.subcategory.image else None

    def __str__(self):
        return f"{self.subcategory.name} ({self.shop.name})"


# ✅ Added image + fallback
class ShopItem(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="shopitems")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="shopitems")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    available_quantity = models.PositiveIntegerField(default=0)
    available_from = models.TimeField(null=True, blank=True)
    available_till = models.TimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='shopitem_images/', blank=True, null=True)

    class Meta:
        unique_together = ('shop', 'item')

    def __str__(self):
        return f"{self.item.name} @ {self.shop.name}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        return self.item.image.url if self.item.image else None

    @property
    def gst_percent(self):
        if self.item.hsn and self.item.hsn.gst:
            return Decimal(self.item.hsn.gst)
        return Decimal('0')

    def calculate_taxable_and_gst(self):
        gst_percent = self.gst_percent
        if gst_percent > 0:
            taxable = (self.total_amount * 100 / (100 + gst_percent)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            gst_amount = (self.total_amount - taxable).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return taxable, gst_amount
        else:
            return self.total_amount, Decimal('0.00')

    @property
    def active_offer(self):
        return self.offers.filter(active=True).first()

    def get_offer_price(self):
        offer = self.active_offer
        if offer:
            discounted_price = (self.total_amount * (offer.offer_pct) / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            return self.total_amount - discounted_price
        return self.total_amount


class ShopItemOffer(models.Model):
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name="offers")
    offer_starting_datetime = models.DateTimeField()
    offer_ending_datetime = models.DateTimeField()
    offer_pct = models.DecimalField(max_digits=5, decimal_places=2)
    max_quantity = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Offer {self.offer_pct}% for {self.shop_item.item.name} in {self.shop_item.shop.name}"
