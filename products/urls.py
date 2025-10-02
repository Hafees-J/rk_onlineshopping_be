from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet,
    SubCategoryViewSet,
    ItemViewSet,
    ShopItemViewSet,
    ShopItemOfferViewSet,
    SubCategoryPerCategoryView,
    ItemPerSubCategoryView,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename="category")
router.register(r'subcategories', SubCategoryViewSet, basename="subcategory")
router.register(r'items', ItemViewSet, basename="item")
router.register(r'shop-items', ShopItemViewSet, basename="shopitem")
router.register(r'shop-item-offers', ShopItemOfferViewSet, basename="shopitemoffer")

urlpatterns = [
    path("", include(router.urls)),

    path("subcategories-per-category/<int:category_id>/", SubCategoryPerCategoryView.as_view(), name="subcategories-per-category"),
    path("items-per-subcategory/<int:subcategory_id>/", ItemPerSubCategoryView.as_view(), name="items-per-subcategory"),
]
