from rest_framework import viewsets, permissions, generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Category, SubCategory, Item, ShopItem, ShopItemOffer
from .serializers import (
    CategorySerializer,
    SubCategorySerializer,
    ItemSerializer,
    ShopItemSerializer,
    ShopItemOfferSerializer,
)

# ---------------- PERMISSIONS -----------------
class IsShopAdmin(permissions.BasePermission):
    """Only branch admins can access"""
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


# ---------------- BRANCH-SPECIFIC MODELS -----------------
class ShopItemViewSet(viewsets.ModelViewSet):
    serializer_class = ShopItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsShopAdmin]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            # Only items belonging to branches owned by this admin
            return ShopItem.objects.filter(shop__owner=user)
        return ShopItem.objects.none()

    def perform_create(self, serializer):
        shop = serializer.validated_data.get("shop")
        if shop.owner != self.request.user:
            raise PermissionDenied("You do not own this branch.")
        serializer.save()

    def perform_update(self, serializer):
        shop = serializer.validated_data.get("shop")
        if shop.owner != self.request.user:
            raise PermissionDenied("You do not own this branch.")
        serializer.save()


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
