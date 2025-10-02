from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Order
from .serializers import OrderSerializer, DistanceInputSerializer
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from shop.models import Branch
from rest_framework.response import Response
from .utils import get_distance_duration


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "customer"
        )


class IsBranchAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "shopadmin"
        )


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if getattr(user, "role", None) == "customer":
            return Order.objects.filter(customer=user)

        if getattr(user, "role", None) == "shopadmin":
            return Order.objects.filter(branch__owner=user)

        return Order.objects.none()


# ---------------- Google Distance + Delivery Charge API ---------------- #
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_delivery_distance(request):
    """
    Calculate distance, duration, and delivery charge.
    Input: user_lat, user_lng, shop_lat, shop_lng, branch_id, total_order_amount
    """
    serializer = DistanceInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    required_fields = ['user_lat', 'user_lng', 'shop_lat', 'shop_lng', 'branch_id', 'total_order_amount']
    if not all(field in data for field in required_fields):
        return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

    # Get distance & duration from Google API
    result = get_distance_duration(
        lat1=data['shop_lat'],
        lng1=data['shop_lng'],
        lat2=data['user_lat'],
        lng2=data['user_lng']
    )
    if not result:
        return Response({"error": "Failed to fetch distance from Google API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Convert distance to km
    distance_km = result['distance_value'] / 1000

    # Get branch and delivery condition
    branch = get_object_or_404(Branch, id=data['branch_id'])
    condition = branch.delivery_conditions.first()
    if not condition:
        return Response({"error": "Delivery condition not set for this branch"}, status=status.HTTP_400_BAD_REQUEST)

    total_amount = data['total_order_amount']
    delivery_charge = None
    delivery_available = True
    message = "Delivery available"

    # Delivery charge calculation logic
    if distance_km > float(condition.maximum_distance):
        delivery_available = False
        delivery_charge = None
        message = "Delivery not available in this range"
    else:
        if distance_km <= float(condition.free_delivery_distance) and total_amount >= float(condition.free_delivery_amount):
            delivery_charge = 0
        else:
            delivery_charge = round(distance_km * float(condition.per_km_charge), 2)

    response = {
        "distance_text": result['distance_text'],
        "distance_value_m": result['distance_value'],
        "duration_text": result['duration_text'],
        "duration_value_s": result['duration_value'],
        "delivery_available": delivery_available,
        "delivery_charge": delivery_charge,
        "message": message
    }

    return Response(response, status=status.HTTP_200_OK)