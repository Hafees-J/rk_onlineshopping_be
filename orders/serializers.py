from decimal import Decimal
from rest_framework import serializers
from user.serializers import AddressSerializer
from .models import Order, OrderItem
from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)
    price = serializers.SerializerMethodField()
    display_image = serializers.SerializerMethodField()  # ✅ added

    shop_id = serializers.IntegerField(source="shop_item.shop.id", read_only=True)
    shop_name = serializers.CharField(source="shop_item.shop.name", read_only=True)
    shop_lat = serializers.SerializerMethodField()
    shop_lng = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "shop_item",
            "shop_item_name",
            "quantity",
            "price",
            "shop_id",
            "shop_name",
            "shop_lat",
            "shop_lng",
            "display_image",  # ✅ added
        ]

    def get_price(self, obj):
        return obj.shop_item.get_offer_price()

    def get_shop_lat(self, obj):
        lat = getattr(obj.shop_item.shop, "latitude", None)
        return float(lat) if lat else None

    def get_shop_lng(self, obj):
        lng = getattr(obj.shop_item.shop, "longitude", None)
        return float(lng) if lng else None

    def get_display_image(self, obj):
        """Return shop item image or fallback to base item image."""
        shop_item = obj.shop_item
        if shop_item.image:
            return shop_item.image.url if hasattr(shop_item.image, "url") else shop_item.image
        elif shop_item.item.image:
            return shop_item.item.image.url if hasattr(shop_item.item.image, "url") else shop_item.item.image
        return None


    
class OrderItemSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)
    subtotal = serializers.SerializerMethodField()
    taxable_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "shop_item",
            "shop_item_name",
            "quantity",
            "price",
            "taxable_amount",
            "gst",
            "subtotal",
        ]
        read_only_fields = ["taxable_amount", "gst", "subtotal"]

    def get_subtotal(self, obj):
        return (obj.price * obj.quantity).quantize(Decimal("0.01"))


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    items_details = OrderItemSerializer(source="items", many=True, read_only=True)

    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    customer_mobile = serializers.CharField(source="customer.mobile_number", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "customer_mobile",
            "shop",
            "shop_name",
            "status",
            "payment_status",
            "created_at",
            "updated_at",
            "items",
            "items_details",
            "total_price",
            "taxable_total",
            "gst",
            "delivery_charge",
            "delivery_address",
        ]
        read_only_fields = [
            "status",
            "payment_status",
            "created_at",
            "updated_at",
            "items_details",
            "total_price",
            "taxable_total",
            "gst",
            "delivery_charge",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.calculate_totals()
        order.save(update_fields=["total_price", "gst", "taxable_total", "delivery_charge"])
        return order


class OrderDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    customer_mobile = serializers.CharField(source="customer.mobile_number", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address_details = AddressSerializer(source="delivery_address", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_name",
            "customer_email",
            "customer_mobile",
            "shop_name",
            "status",
            "payment_status",
            "created_at",
            "updated_at",
            "items",
            "taxable_total",
            "gst",
            "delivery_charge",
            "total_price",
            "delivery_address_details",
        ]

class DistanceInputSerializer(serializers.Serializer):
    user_lat = serializers.FloatField()
    user_lng = serializers.FloatField()
    shop_lat = serializers.FloatField()
    shop_lng = serializers.FloatField()
    shop_id = serializers.IntegerField()  # ID of the Shop for delivery condition
    total_order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
