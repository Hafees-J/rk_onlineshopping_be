from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeliveryConditionViewSet, ShopViewSet, BranchViewSet, MyBranchView

router = DefaultRouter()
router.register(r'delivery-conditions', DeliveryConditionViewSet, basename="delivery-conditions")
router.register(r"shops", ShopViewSet, basename="shops")
router.register(r"branches", BranchViewSet, basename="branches")

urlpatterns = [
    path("", include(router.urls)),

    path("my-branch/", MyBranchView.as_view(), name="my-branch"),
]
