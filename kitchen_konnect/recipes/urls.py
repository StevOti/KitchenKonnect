from django.urls import path
from .views import ProtectedRecipeView

urlpatterns = [
    path('protected/', ProtectedRecipeView.as_view(), name='recipes-protected'),
]
