from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import CustomerRegisterView, CustomTokenObtainPairView

urlpatterns = [
    # Customer registration
    path('register/', CustomerRegisterView.as_view(), name='customer-register'),

    # JWT login
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
