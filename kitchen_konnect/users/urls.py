from django.urls import path
from .views import RegisterView, UserDetailView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    # Simple token endpoint (DRF authtoken)
    path('token/', obtain_auth_token, name='api_token_auth'),
]

try:
    # include JWT token endpoints only if simplejwt is installed
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )

    urlpatterns += [
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]
except Exception:
    # simplejwt not available; token endpoints will not be registered
    pass
