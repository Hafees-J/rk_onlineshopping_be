from rest_framework import serializers
from django.utils import timezone
from .models import Category, ShopSubCategory, SubCategory, Item, ShopItem, ShopItemOffer


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image']


class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'category_name', 'name', 'description', 'image']


class ItemSerializer(serializers.ModelSerializer):
    subcategory_name = serializers.CharField(source="subcategory.name", read_only=True)
    category_name = serializers.CharField(source="subcategory.category.name", read_only=True)
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Item
        fields = ['id', 'subcategory', 'subcategory_name', 'category_name',
                  'name', 'description', 'image']


class ShopItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = ShopItem
        fields = [
            'id', 'shop', 'item', 'item_name', 'total_amount', 
             'discount_amount',
            'available_quantity', 'available_from', 'available_till', 'is_available'
        ]
        read_only_fields = [ 'discount_amount', 'item_name']

    def get_discount_amount(self, obj):
        """Return the offer price for UI highlighting (single-unit)."""
        return obj.get_offer_price()



class ShopItemOfferSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)

    class Meta:
        model = ShopItemOffer
        fields = ['id', 'shop_item', 'shop_item_name',
                  'offer_starting_datetime', 'offer_ending_datetime', 'offer_pct', 'active']


class AvailableSubCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="subcategory.id")
    name = serializers.CharField(source="subcategory.name")

    class Meta:
        model = ShopSubCategory
        fields = ["id", "name"]


class CustomerShopItemSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name", read_only=True)
    shop_name = serializers.CharField(source="shop.name", read_only=True)
    offer_pct = serializers.SerializerMethodField()
    discount_amount = serializers.SerializerMethodField()

    class Meta:
        model = ShopItem
        fields = [
            'id', 'shop', 'shop_name', 'item', 'item_name',
            'total_amount', 'available_quantity', 'is_available',
            'offer_pct', 'discount_amount'
        ]

    def get_offer_pct(self, obj):
        now = timezone.now()
        offer = obj.offers.filter(
            offer_starting_datetime__lte=now,
            offer_ending_datetime__gte=now
        ).first()
        return offer.offer_pct if offer else None
    
    def get_discount_amount(self, obj):
        """Return the offer price for UI highlighting (single-unit)."""
        return obj.get_offer_price()