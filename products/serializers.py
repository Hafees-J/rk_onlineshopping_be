from rest_framework import serializers
from .models import Category, SubCategory, Item, ShopItem, ShopItemOffer


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
    shop_name = serializers.CharField(source="shop.name", read_only=True)

    class Meta:
        model = ShopItem
        fields = ['id', 'shop', 'shop_name', 'item', 'item_name',
                  'price', 'available_quantity', 'available_from', 'available_till']


class ShopItemOfferSerializer(serializers.ModelSerializer):
    shop_item_name = serializers.CharField(source="shop_item.item.name", read_only=True)

    class Meta:
        model = ShopItemOffer
        fields = ['id', 'shop_item', 'shop_item_name',
                  'offer_starting_datetime', 'offer_ending_datetime', 'offer_price']
