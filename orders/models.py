from django.db import models
from shop.models import Shop
from products.models import ShopItem
from user.models import Address, User


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("preparing", "Preparing"),
        ("out_for_delivery", "Out for Delivery"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )

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
    delivery_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders"
    )
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        total_price = 0
        total_gst = 0

        for item in self.items.all():
            total_price += item.price * item.quantity
            total_gst += item.gst

        delivery_charge = 0
        if self.shop and self.shop.delivery_conditions.exists():
            cond = self.shop.delivery_conditions.first()
            delivery_charge = cond.free_delivery_amount  # adjust logic if needed

        self.gst = total_gst
        self.delivery_charge = delivery_charge
        self.total_price = total_price + total_gst + delivery_charge

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # ensure PK exists
        self.calculate_totals()
        super().save(update_fields=["total_price", "gst", "delivery_charge"])

    def __str__(self):
        return f"Order {self.id} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    shop_item = models.ForeignKey(ShopItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_gst(self):
        if hasattr(self.shop_item.item, "hsn") and self.shop_item.item.hsn:
            gst_percent = self.shop_item.item.hsn.igst or 0
            return (self.price * self.quantity * gst_percent) / 100
        return 0

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.shop_item.price
        self.gst = self.calculate_gst()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.shop_item.item.name}"
