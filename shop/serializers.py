from rest_framework import serializers
from .models import Shop, DeliveryCondition

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = [
            "id",
            "shop_type",
            "name",
            "owner",
            "gst_number",
            "contact_number",
            "address",
            "location",
            "pincode",
            "latitude",
            "longitude",
            "is_active",
            "image",
        ]
        read_only_fields = ["id", "owner"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)



class DeliveryConditionSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = DeliveryCondition
        fields = [
            "id",
            "shop_name",
            "free_delivery_amount",
            "free_delivery_distance",
            "maximum_distance",
            "per_km_charge",
        ]
        read_only_fields = ["id", "shop_name"]



class MyShopSerializer(serializers.ModelSerializer):
    shop_id = serializers.IntegerField(source="id", read_only=True)
    shop_name = serializers.CharField(source="name", read_only=True)

    class Meta:
        model = Shop
        fields = ["shop_id", "shop_name", "is_active"]
