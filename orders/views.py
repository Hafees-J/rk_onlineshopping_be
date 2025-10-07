from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Order, Cart, OrderItem
from .serializers import OrderSerializer, DistanceInputSerializer, CartSerializer
from shop.models import Shop
from .utils import get_distance_duration
from rest_framework.decorators import action

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only cart items for the logged-in user"""
        return Cart.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        """Create or update cart item"""
        customer = self.request.user
        shop_item = serializer.validated_data["shop_item"]
        quantity = serializer.validated_data.get("quantity", 1)
        reset = self.request.data.get("reset", False)

        # Get all current items in user's cart
        existing_cart_items = Cart.objects.filter(customer=customer)

        # If there are existing items, ensure same shop
        if existing_cart_items.exists():
            existing_shop = existing_cart_items.first().shop_item.shop
            if shop_item.shop != existing_shop:
                # Different shop detected
                if not reset:
                    # Ask confirmation from frontend
                    return {
                        "requires_reset": True,
                        "detail": "Your cart contains items from another restaurant. Do you want to reset it to add this item?"
                    }

                # If reset=True, clear cart before adding new item
                existing_cart_items.delete()

        # Add or update item in cart
        cart_item, created = Cart.objects.get_or_create(
            customer=customer,
            shop_item=shop_item,
            defaults={"quantity": quantity},
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return cart_item

    def create(self, request, *args, **kwargs):
        """Handle cart add requests with shop validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = self.perform_create(serializer)

        # If perform_create returned a warning dict
        if isinstance(result, dict) and result.get("requires_reset"):
            return Response(result, status=status.HTTP_409_CONFLICT)  # 409 = Conflict

        # Otherwise normal response
        read_serializer = self.get_serializer(result)
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Checkout the current cart"""
        customer = request.user
        cart_items = Cart.objects.filter(customer=customer)

        if not cart_items.exists():
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure all items belong to the same shop
        shop = cart_items.first().shop_item.shop

        # Create the order
        order = Order.objects.create(customer=customer, shop=shop)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                shop_item=item.shop_item,
                quantity=item.quantity,
                price=item.shop_item.get_offer_price(),
            )

        order.calculate_totals()
        order.save()

        # Clear cart after checkout
        cart_items.delete()

        return Response({"message": "Order placed successfully!", "order_id": order.id})


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "role", None) == "customer"
        )


class IsShopAdmin(permissions.BasePermission):
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
            return Order.objects.filter(shop__owner=user)

        return Order.objects.none()


# ---------------- Google Distance + Delivery Charge API ---------------- #
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def calculate_delivery_distance(request):
    """
    Calculate distance, duration, and delivery charge.
    Input: user_lat, user_lng, shop_lat, shop_lng, shop_id, total_order_amount
    """
    serializer = DistanceInputSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    required_fields = ['user_lat', 'user_lng', 'shop_lat', 'shop_lng', 'shop_id', 'total_order_amount']
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

    # Get Shop and delivery condition
    shop = get_object_or_404(Shop, id=data['shop_id'])
    condition = shop.delivery_conditions.first()
    if not condition:
        return Response({"error": "Delivery condition not set for this Shop"}, status=status.HTTP_400_BAD_REQUEST)

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
