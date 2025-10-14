from decimal import ROUND_HALF_UP, Decimal
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
    taxable_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        total_inclusive = Decimal("0.00")
        total_gst = Decimal("0.00")
        total_taxable = Decimal("0.00")

        for item in self.items.all():
            total_inclusive += item.subtotal
            total_gst += item.gst
            total_taxable += item.taxable_amount

        if not self.delivery_charge:
            self.delivery_charge = Decimal("0.00")

        # Use delivery conditions if not set
        if self.delivery_charge == Decimal("0.00") and self.shop and self.shop.delivery_conditions.exists():
            cond = self.shop.delivery_conditions.first()
            if hasattr(cond, "delivery_charge"):
                self.delivery_charge = Decimal(str(cond.delivery_charge))

        self.gst = total_gst.quantize(Decimal("0.01"))
        self.taxable_total = total_taxable.quantize(Decimal("0.01"))
        self.total_price = (total_inclusive + self.delivery_charge).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        self.calculate_totals()
        super().save(update_fields=["total_price", "gst", "taxable_total", "delivery_charge", "updated_at"])

    def __str__(self):
        return f"Order {self.id} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Inclusive of GST
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_gst(self):
        """Extract GST portion and taxable amount from a GST-inclusive price."""
        hsn = getattr(self.shop_item.item, "hsn", None)
        gst_percent = Decimal(hsn.gst) if hsn and getattr(hsn, "gst", None) is not None else Decimal("0.00")

        divisor = (Decimal("100.00") + gst_percent) / Decimal("100.00")

        # Price already includes GST
        taxable_per_unit = (self.price / divisor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        gst_per_unit = (self.price - taxable_per_unit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        self.taxable_amount = (taxable_per_unit * self.quantity).quantize(Decimal("0.01"))
        self.gst = (gst_per_unit * self.quantity).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):
        self.calculate_gst()
        super().save(*args, **kwargs)

    @property
    def subtotal(self):
        """Total amount for this item (inclusive of GST)."""
        return (self.price * self.quantity).quantize(Decimal("0.01"))

    def __str__(self):
        return f"{self.quantity} x {self.shop_item.item.name}"


