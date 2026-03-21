"""
Error Handling Tests
====================
Demonstrates custom exception handler responses for various error scenarios.
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from vendors.models import Vendor

User = get_user_model()


class ErrorHandlingTestCase(APITestCase):
    """Test custom exception handler responses"""

    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='customer'
        )
        self.vendor_user = User.objects.create_user(
            username='vendoruser',
            email='vendor@example.com',
            password='vendorpass123',
            role='vendor'
        )

        def test_401_missing_authentication(self):
            """Test 401 error when authorization header is missing"""
            response = self.client.get('/orders/orders/')
        
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(response.data['code'], 'authentication_failed')
            self.assertEqual(response.data['status'], 401)
            self.assertIn('error', response.data)

        def test_401_error_response_structure(self):
            """Verify 401 error has correct response structure"""
            response = self.client.get('/orders/orders/')
        
            self.assertIn('error', response.data)
            self.assertIn('code', response.data)
            self.assertIn('status', response.data)
            self.assertIsInstance(response.data['error'], str)
            self.assertIsInstance(response.data['code'], str)
            self.assertIsInstance(response.data['status'], int)
            self.assertEqual(response.status_code, response.data['status'])

    def test_404_not_found(self):
            """Test 404 error for non-existent resource"""
            self.client.force_authenticate(self.user)
            response = self.client.get('/products/products/99999/')
        
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data['code'], 'not_found')
            self.assertEqual(response.data['status'], 404)

    def test_404_error_response_structure(self):
            """Verify 404 error response structure"""
            self.client.force_authenticate(self.user)
            response = self.client.get('/products/products/99999/')
        
            self.assertIn('error', response.data)
            self.assertIn('code', response.data)
            self.assertIn('status', response.data)
            self.assertEqual(response.status_code, response.data['status'])

    def test_chat_room_not_found(self):
            """Test 404 error for non-existent chat room"""
            self.client.force_authenticate(self.user)
            response = self.client.get('/api/chat/rooms/99999/')
        
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
            self.assertEqual(response.data['code'], 'not_found')

    def test_error_codes_are_consistent(self):
            """Verify error codes are consistent across different error types"""
            response_401 = self.client.get('/orders/orders/')
            self.assertIsNotNone(response_401.data['code'])
        
            self.client.force_authenticate(self.user)
            response_404 = self.client.get('/products/products/99999/')
            self.assertIsNotNone(response_404.data['code'])
        
            valid_codes = ['authentication_failed', 'not_found', 'validation_error', 
                           'permission_denied', 'server_error', 'internal_error']
            self.assertIn(response_401.data['code'], valid_codes)
            self.assertIn(response_404.data['code'], valid_codes)

        def test_error_messages_are_user_friendly(self):
            """Verify error messages are user-friendly strings"""
            response = self.client.get('/orders/orders/')
        
            self.assertIsInstance(response.data['error'], str)
            self.assertGreater(len(response.data['error']), 0)
            self.assertNotIn('traceback', response.data['error'].lower())
    # ========================
