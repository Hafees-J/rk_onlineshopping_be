from rest_framework import serializers
from .models import Shop, Branch, DeliveryCondition

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ["id", "name", "shop_type"]


class BranchSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)   # nested shop details
    shop_id = serializers.PrimaryKeyRelatedField(
        queryset=Shop.objects.all(), source="shop", write_only=True
    )

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "shop",
            "shop_id",
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
        read_only_fields = ["owner"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class DeliveryConditionSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source="branch.name", read_only=True)

    class Meta:
        model = DeliveryCondition
        fields = [
            "id",
            "branch",
            "branch_name",
            "free_delivery_amount",
            "free_delivery_distance",
            "maximum_distance",
            "per_km_charge",
        ]
        read_only_fields = ["id", "branch_name"]


class MyBranchSerializer(serializers.ModelSerializer):
    shop_id = serializers.IntegerField(source="shop.id", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = Branch
        fields = ["id", "name", "shop_id", "shop_name", "is_active"]