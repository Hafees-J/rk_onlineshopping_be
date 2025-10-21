from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AvailableSubCategoriesView,
    CustomerShopItemsView,
    HSNViewSet,
    ShopsBySubCategoryView,
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
router.register(r'hsn', HSNViewSet, basename='hsn')
router.register(r'items', ItemViewSet, basename="item")
router.register(r'shop-items', ShopItemViewSet, basename="shopitem")
router.register(r'shop-item-offers', ShopItemOfferViewSet, basename="shopitemoffer")

urlpatterns = [


    path(
        "subcategories-per-category/<int:category_id>/",
        SubCategoryPerCategoryView.as_view(),
        name="subcategories-per-category"
    ),
    path(
        "items-per-subcategory/<int:subcategory_id>/",
        ItemPerSubCategoryView.as_view(),
        name="items-per-subcategory"
    ),
    path(
        "shops/by-subcategory/<int:subcategory_id>/",
        ShopsBySubCategoryView.as_view(),
        name="shops-by-subcategory"
    ),
    path("subcategories/available/", AvailableSubCategoriesView.as_view(), name="available-subcategories"),

    path("shops/<int:shop_id>/items/", CustomerShopItemsView.as_view(), name="customer-shop-items"),

    path("", include(router.urls)),
]
