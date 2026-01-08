from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.conf import settings

from .serializers import (
	RegisterSerializer,
	UserSerializer,
	AdminUserSerializer,
	VerificationRequestSerializer,
)
from django.contrib.auth import get_user_model
from .models import VerificationRequest

User = get_user_model()
from .permissions import IsNutritionist, IsRegulator, IsAdminRole, IsAdminLevel
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie, csrf_exempt
from django.middleware.csrf import get_token

logger = logging.getLogger('users.auth')


class RegisterView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]
	throttle_scope = 'register'

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
		refresh_str = None
		try:
			from rest_framework_simplejwt.tokens import RefreshToken

			refresh = RefreshToken.for_user(user)
			payload['access'] = str(refresh.access_token)
			# Do NOT include the refresh token in the JSON payload; we'll set it as an HttpOnly cookie only
			refresh_str = str(refresh)
		except Exception:
			# simplejwt not installed or failed; ignore
			pass

		headers = self.get_success_headers(serializer.data)
		# If simplejwt provided a refresh token, set it as an HttpOnly cookie
		resp = Response(payload, status=status.HTTP_201_CREATED, headers=headers)
		try:
			if refresh_str:
				# determine max_age from SIMPLE_JWT settings if present
				max_age = None
				if getattr(settings, 'SIMPLE_JWT', None) and isinstance(settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'), type):
					try:
						max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
					except Exception:
						max_age = None
				# In development allow cross-site cookie by using SameSite=None so dev frontends can call API
				same_site_value = 'None' if settings.DEBUG else 'Lax'
				logger.info('Setting refresh cookie for user_id=%s secure=%s samesite=%s', user.id, not settings.DEBUG, same_site_value)
				resp.set_cookie(
					'refresh',
					refresh_str,
					httponly=True,
					secure=not settings.DEBUG,
					samesite=same_site_value,
					path='/',
					max_age=max_age,
				)
		except Exception:
			pass
		return resp


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


@method_decorator(csrf_protect, name='dispatch')
class CookieTokenObtainPairView(TokenObtainPairView):
	permission_classes = (AllowAny,)
	throttle_scope = 'login'

	def post(self, request, *args, **kwargs):
		# Delegate to super to obtain tokens
		response = super().post(request, *args, **kwargs)
		try:
			data = response.data
			refresh = data.get('refresh')
			access = data.get('access')
			if refresh:
				max_age = None
				if getattr(settings, 'SIMPLE_JWT', None) and isinstance(settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'), type):
					try:
						max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
					except Exception:
						max_age = None
				# choose SameSite for dev vs prod
				same_site_value = 'None' if settings.DEBUG else 'Lax'
				logger.info('Issuing cookie refresh (login) secure=%s samesite=%s', not settings.DEBUG, same_site_value)
				resp = Response({'access': access}, status=response.status_code)
				resp.set_cookie('refresh', refresh, httponly=True, secure=not settings.DEBUG, samesite=same_site_value, path='/', max_age=max_age)
				return resp
		except Exception:
			pass
		return response


@method_decorator(csrf_protect, name='dispatch')
class CookieTokenRefreshView(TokenRefreshView):
	permission_classes = (AllowAny,)
	throttle_scope = 'refresh'

	def post(self, request, *args, **kwargs):
		# Prefer refresh token from cookie if not supplied in body
		data = request.data.copy() if hasattr(request, 'data') else {}
		if not data.get('refresh'):
			cookie_refresh = request.COOKIES.get('refresh')
			if cookie_refresh:
				data['refresh'] = cookie_refresh

		serializer = TokenRefreshSerializer(data=data)
		serializer.is_valid(raise_exception=True)
		access = serializer.validated_data.get('access')
		resp = Response({'access': access}, status=status.HTTP_200_OK)
		# If rotation provided a new refresh token, set it
		if 'refresh' in serializer.validated_data:
			new_refresh = serializer.validated_data['refresh']
			max_age = None
			if getattr(settings, 'SIMPLE_JWT', None) and isinstance(settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'), type):
				try:
					max_age = int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
				except Exception:
					max_age = None
			# choose SameSite for dev vs prod
			same_site_value = 'None' if settings.DEBUG else 'Lax'
			logger.info('Rotated refresh cookie secure=%s samesite=%s', not settings.DEBUG, same_site_value)
			resp.set_cookie('refresh', new_refresh, httponly=True, secure=not settings.DEBUG, samesite=same_site_value, path='/', max_age=max_age)
		return resp


class LogoutView(APIView):
	permission_classes = (permissions.IsAuthenticated,)

	def post(self, request, *args, **kwargs):
		# Blacklist refresh token if provided in cookie or body
		refresh_token = request.COOKIES.get('refresh') or request.data.get('refresh')
		if refresh_token:
			try:
				token = RefreshToken(refresh_token)
				token.blacklist()
			except Exception:
				pass
		resp = Response(status=status.HTTP_204_NO_CONTENT)
		# Remove cookie
		resp.delete_cookie('refresh', path='/')
		return resp


class NonCookieTokenRefreshView(TokenRefreshView):
	"""Refresh endpoint intended for non-browser clients (mobile/CI).

	Requires an `Authorization` header to reduce accidental browser usage.
	"""
	permission_classes = (AllowAny,)

	def post(self, request, *args, **kwargs):
		# Require Authorization header for extra assurance this is a non-browser client
		if not request.META.get('HTTP_AUTHORIZATION'):
			return Response({'detail': 'Authorization header required for non-cookie refresh.'}, status=status.HTTP_401_UNAUTHORIZED)
		return super().post(request, *args, **kwargs)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CsrfTokenView(APIView):
	"""Simple endpoint that ensures a CSRF cookie is set and returns the token."""
	permission_classes = (AllowAny,)

	def get(self, request, *args, **kwargs):
		token = get_token(request)
		return Response({'csrf': token})


# Do NOT exempt cookie endpoints from CSRF in any environment; keep protection enabled.

# (Removed temporary unconditional csrf_exempt to restore normal CSRF behavior.)
