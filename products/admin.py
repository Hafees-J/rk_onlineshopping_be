from django.contrib import admin
from .models import Category, SubCategory, Item, ShopItem, ShopItemOffer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    raw_id_fields = ('category',)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subcategory')
    list_filter = ('subcategory',)
    search_fields = ('name',)
    raw_id_fields = ('subcategory',)


@admin.register(ShopItem)
class ShopItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'shop', 'price', 'available_quantity', 'available_from', 'available_till')
    list_filter = ('shop', 'item')
    search_fields = ('item__name', 'shop__name')
    raw_id_fields = ('item', 'shop')


@admin.register(ShopItemOffer)
class ShopItemOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop_item', 'offer_price', 'offer_starting_datetime', 'offer_ending_datetime')
    list_filter = ('offer_starting_datetime', 'offer_ending_datetime')
    search_fields = ('shop_item__item__name',)
    raw_id_fields = ('shop_item',)
