from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("shop_item", "quantity", "price")
    can_delete = False  # optional: prevent deletion from admin inline


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "branch", "status", "total_price", "created_at")
    list_filter = ("status", "branch")
    search_fields = ("customer__username", "branch__name")
    inlines = [OrderItemInline]
    readonly_fields = ("total_price",)  # optional: total_price is computed
    date_hierarchy = "created_at"

    def total_price(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())
    total_price.short_description = "Total Price"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "shop_item", "quantity", "price")
    list_filter = ("order__status", "shop_item__shop__name")
    search_fields = ("shop_item__item__name", "order__customer__username")
    raw_id_fields = ("order", "shop_item")
