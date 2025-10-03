from django.contrib import admin
from .models import Category, ShopCategory, ShopSubCategory, SubCategory, Item, ShopItem, ShopItemOffer

admin.site.register(ShopSubCategory)
admin.site.register(ShopCategory)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Item)
admin.site.register(ShopItem)
admin.site.register(ShopItemOffer)
