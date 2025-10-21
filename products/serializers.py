from rest_framework import serializers
from django.utils import timezone
from .models import (
    HSN, Category, SubCategory, Item,
    ShopSubCategory, ShopItem, ShopItemOffer
)


# ---------- BASE MODELS ----------

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image']


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.ImageField(use_url=True, required=False)

    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'category_name', 'name', 'description', 'image']

class HSNSerializer(serializers.ModelSerializer):
    class Meta:
        model = HSN
        fields = ['id', 'hsncode', 'gst']


class ItemSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)
    category_name = serializers.CharField(source="subcategory.category.name", read_only=True)
    image = serializers.ImageField(use_url=True, required=False)
    hsn = HSNSerializer(read_only=True)
    hsn_id = serializers.PrimaryKeyRelatedField(
        queryset=HSN.objects.all(), source="hsn", write_only=True, required=False
    )

    class Meta:
        model = Item
        fields = [
            "id",
            "subcategory",
            "subcategory_name",
            "category_name",
            "name",
            "description",
            "hsn",
            "hsn_id",
            "image",
        ]


# ---------- SHOP LEVEL MODELS ----------

class ShopSubCategorySerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)
    display_image = serializers.SerializerMethodField()

    class Meta:
        model = ShopSubCategory
        fields = ['id', 'shop', 'subcategory', 'subcategory_name', 'image', 'display_image']

    def get_display_image(self, obj):
        """Return shop subcategory image or fallback to base subcategory image."""
        if obj.display_image:
            return obj.display_image
        return None


class ShopItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    discount_amount = serializers.SerializerMethodField()
    display_image = serializers.SerializerMethodField()

    class Meta:
        model = ShopItem
        fields = [
            'id', 'shop', 'item', 'item_name',
            'total_amount', 'discount_amount',
            'available_quantity', 'available_from',
            'available_till', 'is_available',
            'image', 'display_image'
        ]
        read_only_fields = ['discount_amount', 'item_name']

    def get_discount_amount(self, obj):
        """Return the offer price for UI highlighting (single-unit)."""
        return obj.get_offer_price()

    def get_display_image(self, obj):
        """Return shop item image or fallback to base item image."""
        if obj.display_image:
            return obj.display_image
        return None


# ---------- OFFERS ----------

class ShopItemOfferSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)

    class Meta:
        model = ShopItemOffer
        fields = [
            'id', 'shop_item', 'shop_item_name',
            'offer_starting_datetime', 'offer_ending_datetime',
            'offer_pct', 'active'
        ]


# ---------- CUSTOMER SIDE ----------

class CustomerShopItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    offer_pct = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()
    display_image = serializers.SerializerMethodField()

    class Meta:
        model = ShopItem
        fields = [
            'id', 'shop', 'shop_name', 'item', 'item_name',
            'total_amount', 'available_quantity', 'is_available',
            'offer_pct', 'discount_amount', 'display_image'
        ]

    def get_offer_pct(self, obj):
        now = timezone.now()
        offer = obj.offers.filter(
            offer_starting_datetime__lte=now,
            offer_ending_datetime__gte=now
        ).first()
        return offer.offer_pct if offer else None

    def get_discount_amount(self, obj):
        return obj.get_offer_price()

    def get_display_image(self, obj):
        request = self.context.get("request")
        # Priority: ShopItem image -> Base Item image
        image_field = obj.image or obj.item.image
        if image_field:
            return request.build_absolute_uri(image_field.url)
        return None


class AvailableSubCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="subcategory.id")
    name = serializers.CharField(source="subcategory.name")
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShopSubCategory
        fields = ["id", "name", "image"]

    def get_image(self, obj):
        request = self.context.get("request")
        # Priority: ShopSubCategory image -> Base SubCategory image
        image_field = obj.image or obj.subcategory.image
        if image_field:
            return request.build_absolute_uri(image_field.url)
        return None