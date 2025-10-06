from rest_framework import serializers
from .models import Order, OrderItem
from .models import Cart

class CartSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "shop_item", "shop_item_name", "quantity", "price"]

    def get_price(self, obj):
        return obj.shop_item.get_offer_price()

    
class OrderItemSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "shop_item", "shop_item_name", "quantity", "price", "gst"]
        read_only_fields = ["price", "gst"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, write_only=True)
    items_details = OrderItemSerializer(source="items", many=True, read_only=True)

    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    customer_email = serializers.CharField(source="customer.email", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_name",
            "customer_email",
            "shop",
            "shop_name",
            "status",
            "payment_status",
            "created_at",
            "updated_at",
            "items",
            "items_details",
            "total_price",
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
            "gst",
            "delivery_charge",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.save()
        return order


class DistanceInputSerializer(serializers.Serializer):
    user_lat = serializers.FloatField()
    user_lng = serializers.FloatField()
    shop_lat = serializers.FloatField()
    shop_lng = serializers.FloatField()
    shop_id = serializers.IntegerField()  # ID of the Shop for delivery condition
    total_order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
