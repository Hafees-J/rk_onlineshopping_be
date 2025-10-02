from rest_framework import viewsets, generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import DeliveryCondition, Shop, Branch
from .serializers import ShopSerializer, BranchSerializer, DeliveryConditionSerializer, MyBranchSerializer

class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]


class BranchViewSet(viewsets.ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # shopadmins see only their branches, others see all
        if user.role == "shopadmin":
            return Branch.objects.filter(owner=user)
        return Branch.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



# ---------------- DeliveryCondition ViewSet ---------------- #
class DeliveryConditionViewSet(viewsets.ModelViewSet):
    """
    - Customers: read-only access to all delivery conditions.
    - Shop Admins: can view/edit only their branch's condition.
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
            return DeliveryCondition.objects.filter(branch__owner=user)
        elif user.role == "customer":
            return DeliveryCondition.objects.all()
        return DeliveryCondition.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if user.role == "superadmin":
            serializer.save()
        elif user.role == "shopadmin":
            branch = Branch.objects.filter(owner=user).first()
            if not branch:
                raise PermissionDenied("No branch found for this shop admin.")

            if branch.delivery_conditions.exists():
                raise PermissionDenied("This branch already has a delivery condition.")

            serializer.save(branch=branch)
        else:
            raise PermissionDenied("You do not have permission to create delivery conditions.")


class MyBranchView(generics.RetrieveAPIView):
    serializer_class = MyBranchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.role != "shopadmin":
            return Response({"detail": "Only shop admins have branches."}, status=403)

        branch = request.user.branches.filter(is_active=True).first()
        if not branch:
            return Response({"detail": "No active branch found."}, status=404)

        serializer = self.get_serializer(branch)
        return Response(serializer.data)