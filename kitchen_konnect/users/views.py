from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from .serializers import (
	RegisterSerializer,
	UserSerializer,
	ProfileSerializer,
	AdminUserSerializer,
	VerificationRequestSerializer,
)
from django.contrib.auth import get_user_model
from .models import VerificationRequest

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

		# If user requested a non-regular role at registration, create a verification request
		desired = request.data.get('desired_role')
		if desired and desired != User.ROLE_REGULAR:
			VerificationRequest.objects.create(user=user, requested_role=desired, message=request.data.get('verification_message', ''))

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
	# Expose role/admin_level for the authenticated user's profile
	serializer_class = ProfileSerializer
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


class VerificationRequestCreate(generics.CreateAPIView):
	serializer_class = VerificationRequestSerializer
	permission_classes = [permissions.IsAuthenticated]

	def perform_create(self, serializer):
		serializer.save(user=self.request.user)


class VerificationRequestList(generics.ListAPIView):
	"""Admins list verification requests (filter by status via ?status=)."""

	serializer_class = VerificationRequestSerializer
	permission_classes = [IsAdminLevel]
	min_admin_level = 50

	def get_queryset(self):
		qs = VerificationRequest.objects.all()
		status = self.request.query_params.get('status')
		if status:
			qs = qs.filter(status=status)
		return qs


class VerificationRequestReview(generics.UpdateAPIView):
	"""Admin approves/rejects verification requests."""

	serializer_class = VerificationRequestSerializer
	permission_classes = [IsAdminLevel]
	min_admin_level = 50
	queryset = VerificationRequest.objects.all()

	def perform_update(self, serializer):
		instance = serializer.instance
		old_status = instance.status
		serializer.save()
		new_status = serializer.instance.status
		# record reviewer and timestamp
		serializer.instance.reviewed_by = self.request.user
		from django.utils.timezone import now
		serializer.instance.reviewed_at = now()
		serializer.instance.save()
		# When approving, change the user's role/admin_level accordingly
		if old_status != new_status and new_status == VerificationRequest.STATUS_APPROVED:
			user = serializer.instance.user
			req_role = serializer.instance.requested_role
			user.role = req_role
			if req_role == User.ROLE_ADMIN:
				user.admin_level = max(user.admin_level or 0, 100)
			elif req_role == User.ROLE_REGULATOR:
				user.admin_level = max(user.admin_level or 0, 50)
			user.save()
