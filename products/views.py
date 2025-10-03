from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from shop.models import Shop
from shop.serializers import ShopSerializer
from .models import Category, ShopCategory, ShopSubCategory, SubCategory, Item, ShopItem, ShopItemOffer
from .serializers import (
    CategorySerializer,
    SubCategorySerializer,
    ItemSerializer,
    ShopItemSerializer,
    ShopItemOfferSerializer,
)

# ---------------- PERMISSIONS -----------------
class IsShopAdmin(permissions.BasePermission):
    """Only Shop admins can access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, "role", None) == "shopadmin"


# ---------------- GLOBAL MODELS -----------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdmin]


class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdmin]


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdmin]


# ---------------- NEW FILTERED APIs -----------------
class SubCategoryPerCategoryView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return SubCategory.objects.filter(category_id=category_id)


class ItemPerSubCategoryView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        subcategory_id = self.kwargs["subcategory_id"]
        return Item.objects.filter(subcategory_id=subcategory_id)


# ---------------- Shop-SPECIFIC MODELS -----------------
class ShopItemViewSet(viewsets.ModelViewSet):
    serializer_class = ShopItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdmin]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return ShopItem.objects.filter(shop__owner=user)
        return ShopItem.objects.none()

    def perform_create(self, serializer):
        shop = serializer.validated_data.get("shop")
        item = serializer.validated_data.get("item")

        if shop.owner != self.request.user:
            raise PermissionDenied("You do not own this Shop.")

        shopitem = serializer.save()

        # Ensure subcategory exists
        subcategory = item.subcategory
        if subcategory:
            ShopSubCategory.objects.get_or_create(shop=shop, subcategory=subcategory)
            if subcategory.category:
                ShopCategory.objects.get_or_create(shop=shop, category=subcategory.category)

        return shopitem

    def perform_update(self, serializer):
        shop = serializer.validated_data.get("shop")
        item = serializer.validated_data.get("item")

        if shop.owner != self.request.user:
            raise PermissionDenied("You do not own this Shop.")

        shopitem = serializer.save()

        # Also enforce subcategory + category during update
        subcategory = item.subcategory
        if subcategory:
            ShopSubCategory.objects.get_or_create(shop=shop, subcategory=subcategory)
            if subcategory.category:
                ShopCategory.objects.get_or_create(shop=shop, category=subcategory.category)

        return shopitem


class ShopItemOfferViewSet(viewsets.ModelViewSet):
    serializer_class = ShopItemOfferSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdmin]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return ShopItemOffer.objects.filter(shop_item__shop__owner=user)
        return ShopItemOffer.objects.none()

    def perform_create(self, serializer):
        shop_item = serializer.validated_data.get("shop_item")
        if shop_item.shop.owner != self.request.user:
            raise PermissionDenied("You do not own this shop item.")
        serializer.save()

    def perform_update(self, serializer):
        shop_item = serializer.validated_data.get("shop_item")
        if shop_item.shop.owner != self.request.user:
            raise PermissionDenied("You do not own this shop item.")
        serializer.save()


class ShopsBySubCategoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ShopSerializer  # use your existing Shop serializer

    def get_queryset(self):
        subcategory_id = self.kwargs.get("subcategory_id")
        return Shop.objects.filter(
            shopsubcategory__subcategory_id=subcategory_id
        ).distinct()
