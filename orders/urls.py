from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CartViewSet, calculate_delivery_distance

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register("cart", CartViewSet, basename="cart")

urlpatterns = [
    path("calculate-delivery-distance/", calculate_delivery_distance, name="calculate-delivery-distance"),
    path('', include(router.urls)),
]
