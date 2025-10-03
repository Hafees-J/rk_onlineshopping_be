from rest_framework import viewsets, generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import DeliveryCondition, Shop
from .serializers import ShopSerializer, DeliveryConditionSerializer, MyShopSerializer


# ---------------- Shop ViewSet ---------------- #
class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Shop admins see only their shops, others see all
        if user.role == "shopadmin":
            return Shop.objects.filter(owner=user)
        return Shop.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


# ---------------- DeliveryCondition ViewSet ---------------- #
class DeliveryConditionViewSet(viewsets.ModelViewSet):
    """
    - Customers: read-only access to all delivery conditions.
    - Shop Admins: can view/edit only their Shop's condition.
    - Superadmins: full access.
    """
    serializer_class = DeliveryConditionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return DeliveryCondition.objects.none()

        if user.role == "superadmin":
            return DeliveryCondition.objects.all()
        elif user.role == "shopadmin":
            return DeliveryCondition.objects.filter(shop__owner=user)
        elif user.role == "customer":
            return DeliveryCondition.objects.all()
        return DeliveryCondition.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "superadmin":
            serializer.save()
        elif user.role == "shopadmin":
            shop = Shop.objects.filter(owner=user).first()
            if not shop:
                raise PermissionDenied("No shop found for this shop admin.")

            if shop.delivery_conditions.exists():
                raise PermissionDenied("This shop already has a delivery condition.")

            serializer.save(shop=shop)
        else:
            raise PermissionDenied("You do not have permission to create delivery conditions.")


# ---------------- MyShop View ---------------- #
class MyShopView(generics.RetrieveAPIView):
    serializer_class = MyShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != "shopadmin":
            return Response({"detail": "Only shop admins have shops."}, status=403)

        shop = request.user.shops.filter(is_active=True).first()
        if not shop:
            return Response({"detail": "No active shop found."}, status=404)

        serializer = self.get_serializer(shop)
        return Response(serializer.data)
