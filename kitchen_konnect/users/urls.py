from django.urls import path
from .views import RegisterView, UserDetailView
from .views import NutritionistArea, RegulatorArea, AdminArea
from .views import AdminUserList, AdminUserUpdate
from .views import VerificationRequestCreate, VerificationRequestList, VerificationRequestReview

# Base routes
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
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
    # Prefer SimpleJWT if available: register JWT endpoints under /token/
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )

    urlpatterns += [
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    ]
except Exception:
    # Fall back to DRF TokenAuth endpoint when SimpleJWT is not installed
    try:
        from rest_framework.authtoken.views import obtain_auth_token
        urlpatterns += [
            path('token/', obtain_auth_token, name='api_token_auth'),
        ]
    except Exception:
        # Neither token system available; skip registering token endpoints
        pass
