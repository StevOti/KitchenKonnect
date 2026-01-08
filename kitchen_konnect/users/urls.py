from django.urls import path
from .views import RegisterView, UserDetailView, CsrfTokenView
from .views import NutritionistArea, RegulatorArea, AdminArea
from .views import AdminUserList, AdminUserUpdate
from .views import VerificationRequestCreate, VerificationRequestList, VerificationRequestReview

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('csrf/', CsrfTokenView.as_view(), name='csrf-token'),
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
    # Prefer SimpleJWT token endpoints when available
    from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )
    # cookie-aware views (implemented in users.views)
    from .views import CookieTokenObtainPairView, CookieTokenRefreshView, LogoutView

    urlpatterns += [
        path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
            # Non-cookie refresh for non-browser clients (requires Authorization header)
        path('token/refresh-noncookie/', NonCookieTokenRefreshView.as_view(), name='token_refresh_noncookie'),
        path('cookie/token/', CookieTokenObtainPairView.as_view(), name='cookie_token_obtain'),
        path('cookie/refresh/', CookieTokenRefreshView.as_view(), name='cookie_token_refresh'),
        path('cookie/logout/', LogoutView.as_view(), name='cookie_logout'),
    ]
except Exception:
    # Fall back to DRF TokenAuth if simplejwt is not installed
    from rest_framework.authtoken.views import obtain_auth_token

    urlpatterns += [
        path('token/', obtain_auth_token, name='api_token_auth'),
    ]
