"""Error handling tests for custom exception handler"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class ErrorHandlingAPITest(APITestCase):
    """Test custom exception handler with real API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            role='customer'
        )

    def test_401_unauthorized_error(self):
        """Test 401 Unauthorized error response"""
        response = self.client.get('/orders/orders/')
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['code'], 'authentication_failed')
        self.assertEqual(response.data['status'], 401)
        self.assertIn('error', response.data)

    def test_404_not_found_error(self):
        """Test 404 Not Found error response"""
        self.client.force_authenticate(self.user)
        response = self.client.get('/products/products/99999/')
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['code'], 'not_found')
        self.assertEqual(response.data['status'], 404)

    def test_error_response_structure(self):
        """Verify error response has all required fields"""
        response = self.client.get('/orders/orders/')
        
        self.assertIn('error', response.data)
        self.assertIn('code', response.data)
        self.assertIn('status', response.data)
        self.assertEqual(response.status_code, response.data['status'])

    def test_error_codes_are_valid(self):
        """Test that error codes are from approved list"""
        response = self.client.get('/orders/orders/')
        
        valid_codes = [
            'authentication_failed',
            'not_found',
            'validation_error',
            'permission_denied',
            'method_not_allowed',
            'server_error',
            'internal_error'
        ]
        self.assertIn(response.data['code'], valid_codes)
