from rest_framework.test import APITestCase


class RecipesProtectedTest(APITestCase):
    def test_protected_requires_auth(self):
        resp = self.client.get('/api/recipes/protected/')
        # should be unauthorized (401) if not logged in
        self.assertIn(resp.status_code, (401, 403))
from django.test import TestCase

# Create your tests here.
