from rest_framework.test import APITestCase


class HealthProtectedTest(APITestCase):
    def test_protected_requires_auth(self):
        resp = self.client.get('/api/health/protected/')
        self.assertIn(resp.status_code, (401, 403))
from django.test import TestCase

# Create your tests here.
