from django.contrib import admin
from .models import Shop, Branch, DeliveryCondition


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop_type')
    list_filter = ('shop_type',)
    search_fields = ('name',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'shop', 'owner', 'contact_number', 'is_active')
    list_filter = ('is_active', 'shop')
    search_fields = ('name', 'gst_number', 'owner__username')
    raw_id_fields = ('shop', 'owner')

admin.site.register(DeliveryCondition)