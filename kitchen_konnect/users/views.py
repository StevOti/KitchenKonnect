from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .serializers import RegisterSerializer, UserSerializer, AdminUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()
from .permissions import IsNutritionist, IsRegulator, IsAdminRole, IsAdminLevel


class RegisterView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]

	def create(self, request, *args, **kwargs):
		"""Create a user and return an auth token (and JWTs if available).

		Response contains at least `token` (DRF TokenAuth key). If
		`djangorestframework-simplejwt` is installed, also returns
		`access` and `refresh` JWT strings.
		"""
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()

		# Create or get DRF authtoken key
		token_obj, _ = Token.objects.get_or_create(user=user)
		payload = {
			'id': user.id,
			'username': user.username,
			'token': token_obj.key,
		}

		# If simplejwt is available, issue access/refresh tokens as well
		try:
			from rest_framework_simplejwt.tokens import RefreshToken

			refresh = RefreshToken.for_user(user)
			payload['access'] = str(refresh.access_token)
			payload['refresh'] = str(refresh)
		except Exception:
			# simplejwt not installed or failed; ignore
			pass

		headers = self.get_success_headers(serializer.data)
		return Response(payload, status=status.HTTP_201_CREATED, headers=headers)


class UserDetailView(generics.RetrieveAPIView):
	serializer_class = UserSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		return self.request.user


class NutritionistArea(APIView):
	"""Example endpoint that only nutritionists can access."""

	permission_classes = [IsNutritionist]

	def get(self, request, *args, **kwargs):
		return Response({"detail": "nutritionist area"})


class RegulatorArea(APIView):
	permission_classes = [IsRegulator]

	def get(self, request, *args, **kwargs):
		return Response({"detail": "regulator area"})


class AdminArea(APIView):
	# require admin_level >= 50 by default
	permission_classes = [IsAdminLevel]
	min_admin_level = 50

	def get(self, request, *args, **kwargs):
		return Response({"detail": "admin area (min level 50)"})


class AdminUserList(generics.ListAPIView):
	"""List all users (admin-only)."""

	permission_classes = [IsAdminLevel]
	min_admin_level = 50
	serializer_class = AdminUserSerializer

	def get_queryset(self):
		return User.objects.all().order_by('id')


class AdminUserUpdate(generics.UpdateAPIView):
	"""Update role/admin_level for a user (admin-only)."""

	permission_classes = [IsAdminLevel]
	min_admin_level = 50
	serializer_class = AdminUserSerializer
	queryset = User.objects.all()
