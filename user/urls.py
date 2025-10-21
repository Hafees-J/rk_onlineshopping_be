from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import AddressViewSet, ChangePasswordView, CustomerRegisterView, CustomTokenObtainPairView, UserProfileView



router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [

    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
    
    # Customer registration
    path('register/', CustomerRegisterView.as_view(), name='customer-register'),

    # JWT login
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
]
