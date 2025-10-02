from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, calculate_delivery_distance

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path("distance/", calculate_delivery_distance, name="calculate-distance"),
    path('', include(router.urls)),
]
