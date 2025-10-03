from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, calculate_delivery_distance

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path("calculate-delivery-distance/", calculate_delivery_distance, name="calculate-delivery-distance"),
    path('', include(router.urls)),
]
