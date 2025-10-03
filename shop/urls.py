from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryConditionViewSet, ShopViewSet, MyShopView

router = DefaultRouter()
router.register(r'delivery-conditions', DeliveryConditionViewSet, basename="delivery-conditions")
router.register(r'shops', ShopViewSet, basename="shops")

urlpatterns = [
    path("", include(router.urls)),
    path("my-shop/", MyShopView.as_view(), name="my-shop"),
]
