from django.test import TestCase

from rest_framework.test import APITestCase
import importlib.util


class AuthAPITest(APITestCase):
	def setUp(self):
		self.register_url = '/api/auth/register/'
		self.token_url = '/api/auth/token/'
		self.refresh_url = '/api/auth/token/refresh/'
		self.me_url = '/api/auth/me/'
		self.user_data = {
			'username': 'testuser',
			'email': 'testuser@example.com',
			'password': 'strongpassword123',
			'first_name': 'Test',
			'last_name': 'User',
		}
		self.has_simplejwt = importlib.util.find_spec('rest_framework_simplejwt') is not None

	def test_register_and_me_with_available_auth(self):
		# Register user
		resp = self.client.post(self.register_url, self.user_data, format='json')
		self.assertIn(resp.status_code, (200, 201))

		if self.has_simplejwt:
			# JWT flow
			token_resp = self.client.post(self.token_url, {
				'username': self.user_data['username'],
				'password': self.user_data['password'],
			}, format='json')
			self.assertEqual(token_resp.status_code, 200)
			self.assertIn('token', token_resp.data)
			self.assertIn('refresh', token_resp.data)

			access = token_resp.data['access']
			refresh = token_resp.data['refresh']

			# Access protected endpoint with Bearer token
			self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
			me_resp = self.client.get(self.me_url)
			self.assertEqual(me_resp.status_code, 200)
			self.assertEqual(me_resp.data['username'], self.user_data['username'])

			# Refresh token
			refresh_resp = self.client.post(self.refresh_url, {'refresh': refresh}, format='json')
			self.assertEqual(refresh_resp.status_code, 200)
			self.assertIn('access', refresh_resp.data)
		else:
			# session auth fallback
			logged_in = self.client.login(username=self.user_data['username'], password=self.user_data['password'])
			self.assertTrue(logged_in)
			me_resp = self.client.get(self.me_url)
			self.assertEqual(me_resp.status_code, 200)
			self.assertEqual(me_resp.data['username'], self.user_data['username'])

	def test_registration_validation(self):
		# missing password
		bad = {'username': 'u1', 'email': 'u1@example.com'}
		resp = self.client.post(self.register_url, bad, format='json')
		self.assertIn(resp.status_code, (400,))

		# weak password (too short)
		bad2 = {'username': 'u2', 'email': 'u2@example.com', 'password': 'short'}
		resp2 = self.client.post(self.register_url, bad2, format='json')
		self.assertIn(resp2.status_code, (400,))

		# duplicate email
		good = {'username': 'unique1', 'email': 'dup@example.com', 'password': 'strongPass123'}
		r1 = self.client.post(self.register_url, good, format='json')
		self.assertIn(r1.status_code, (200, 201))
		good2 = {'username': 'unique2', 'email': 'dup@example.com', 'password': 'strongPass123'}
		r2 = self.client.post(self.register_url, good2, format='json')
		self.assertIn(r2.status_code, (400,))

	def test_user_serializer_fields(self):
		# ensure serializer exposes expected fields
		from .serializers import UserSerializer
		from django.contrib.auth import get_user_model
		User = get_user_model()
		u = User.objects.create_user(username='seruser', email='s@example.com', password='strongPass123', first_name='S', last_name='U')
		data = UserSerializer(u).data
		self.assertSetEqual(set(data.keys()), {'id', 'username', 'email', 'first_name', 'last_name', 'admin_level', 'role'})