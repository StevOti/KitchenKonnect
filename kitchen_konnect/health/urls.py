from django.urls import path
from .views import ProtectedHealthView

urlpatterns = [
    path('protected/', ProtectedHealthView.as_view(), name='health-protected'),
]
