from django.urls import path
from .views import RegisterView, UserDetailView
from rest_framework.authtoken.views import obtain_auth_token
from .views import NutritionistArea, RegulatorArea, AdminArea
from .views import AdminUserList, AdminUserUpdate
from .views import VerificationRequestCreate, VerificationRequestList, VerificationRequestReview

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    # Simple token endpoint (DRF authtoken)
    path('token/', obtain_auth_token, name='api_token_auth'),
]

urlpatterns += [
    path('nutritionist-area/', NutritionistArea.as_view(), name='nutritionist-area'),
    path('regulator-area/', RegulatorArea.as_view(), name='regulator-area'),
    path('admin-area/', AdminArea.as_view(), name='admin-area'),
]

urlpatterns += [
    path('admin/users/', AdminUserList.as_view(), name='admin-user-list'),
    path('admin/users/<int:pk>/', AdminUserUpdate.as_view(), name='admin-user-update'),
]

urlpatterns += [
    path('verification/', VerificationRequestCreate.as_view(), name='verification-create'),
    path('verification/requests/', VerificationRequestList.as_view(), name='verification-list'),
    path('verification/requests/<int:pk>/', VerificationRequestReview.as_view(), name='verification-review'),
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
