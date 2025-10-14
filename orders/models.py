from decimal import Decimal
from django.db import models
from shop.models import Shop
from products.models import ShopItem
from user.models import Address, User

class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'shop_item')  # prevent duplicates
        ordering = ['-added_at']

    def subtotal(self):
        """Calculate total for this item"""
        price = self.shop_item.get_offer_price()
        return price * self.quantity

    def __str__(self):
        return f"{self.customer.username} - {self.shop_item.item.name} ({self.quantity})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out for Delivery"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="orders", null=True)
    delivery_boy = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
        limit_choices_to={"role": "deliveryboy"},
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        total_price = Decimal('0.00')
        total_gst = Decimal('0.00')

        for item in self.items.all():
            total_price += item.price * item.quantity
            total_gst += item.gst

        # Ensure delivery_charge is Decimal
        if self.delivery_charge is None:
            self.delivery_charge = Decimal('0.00')
        else:
            self.delivery_charge = Decimal(str(self.delivery_charge))

        # Only override delivery_charge if it is 0 (frontend value takes priority)
        if self.delivery_charge == Decimal('0.00') and self.shop and self.shop.delivery_conditions.exists():
            cond = self.shop.delivery_conditions.first()
            self.delivery_charge = Decimal(str(cond.delivery_charge)) if hasattr(cond, "delivery_charge") else Decimal('0.00')

        self.gst = total_gst.quantize(Decimal('0.01'))
        self.total_price = (total_price + self.delivery_charge).quantize(Decimal('0.01'))



    def save(self, *args, **kwargs):
        # When order is first created, it won't have a PK yet
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save first to get a PK if new

        # Calculate totals (items can now be queried)
        self.calculate_totals()

        # Only update the relevant fields to avoid overwriting other changes
        update_fields = ["total_price", "gst", "delivery_charge", "updated_at"]
        super().save(update_fields=update_fields)



    def __str__(self):
        return f"Order {self.id} - {self.customer}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price per unit
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # total gst for this item

    def calculate_gst(self):
        if hasattr(self.shop_item.item, "hsn") and self.shop_item.item.hsn:
            gst_percent = Decimal(self.shop_item.item.hsn.gst or 0)
            return (self.price * self.quantity * gst_percent / 100).quantize(Decimal('0.01'))
        return Decimal('0.00')

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.shop_item.total_amount
        self.gst = self.calculate_gst()
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        return (self.price * self.quantity).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.quantity} x {self.shop_item.item.name}"

