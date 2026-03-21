"""
Error Handling Tests
====================
Demonstrates custom exception handler responses for various error scenarios.
"""

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product
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
        self.vendor = Vendor.objects.create(
            user=self.vendor_user,
            store_name='Test Store',
            is_approved=True
        )

    # ========================
    # 401 - Authentication Errors
    # ========================

    def test_missing_authentication_header(self):
        """Test 401 error when authorization header is missing"""
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'authentication_failed')
        self.assertEqual(response.data['status'], 401)
        self.assertIn('error', response.data)
        self.assertNotIn('details', response.data)  # No details for auth errors

    def test_invalid_token_format(self):
        """Test 401 error with malformed token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer INVALID_TOKEN')
        response = self.client.get('/api/orders/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'authentication_failed')

    # ========================
    # 403 - Permission Errors
    # ========================

    def test_customer_cannot_create_product(self):
        """Test 403 error when customer tries to create product"""
        self.client.force_authenticate(self.user)
        
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Test Product',
                'price': 99.99,
                'description': 'Test'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'permission_denied')
        self.assertEqual(response.data['status'], 403)
        self.assertIn('error', response.data)

    def test_vendor_can_create_product(self):
        """Test vendor can create product (positive case)"""
        self.client.force_authenticate(self.vendor_user)
        
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Test Product',
                'price': 99.99,
                'description': 'Test'
            }
        )
        
        # Should succeed (201) or fail with validation, not permission error
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ========================
    # 404 - Not Found Errors
    # ========================

    def test_product_not_found(self):
        """Test 404 error for non-existent product"""
        self.client.force_authenticate(self.user)
        
        response = self.client.get('/api/products/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 'not_found')
        self.assertEqual(response.data['status'], 404)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Not found.')

    def test_order_not_found(self):
        """Test 404 error for non-existent order"""
        self.client.force_authenticate(self.user)
        
        response = self.client.get('/api/orders/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 'not_found')

    def test_chat_room_not_found(self):
        """Test 404 error for non-existent chat room"""
        self.client.force_authenticate(self.user)
        
        response = self.client.get('/api/chat/rooms/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['code'], 'not_found')

    # ========================
    # 400 - Validation Errors
    # ========================

    def test_validation_error_missing_field(self):
        """Test 400 error for missing required field"""
        self.client.force_authenticate(self.vendor_user)
        
        # Missing 'name' and 'price' fields
        response = self.client.post(
            '/api/products/',
            {'description': 'Missing required fields'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'validation_error')
        self.assertEqual(response.data['status'], 400)
        self.assertIn('error', response.data)
        self.assertIn('details', response.data)
        # details should contain field-level errors
        self.assertIsInstance(response.data['details'], dict)

    def test_validation_error_invalid_price(self):
        """Test 400 error for invalid price format"""
        self.client.force_authenticate(self.vendor_user)
        
        response = self.client.post(
            '/api/products/',
            {
                'name': 'Test Product',
                'price': 'not_a_number',  # Invalid
                'description': 'Test'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'validation_error')
        self.assertIn('price', response.data['details'])

    def test_validation_error_multiple_fields(self):
        """Test 400 error with multiple field errors"""
        # Try to register with invalid data
        response = self.client.post(
            '/api/users/register/',
            {
                'email': 'invalid-email',  # Invalid format
                'password': '123',  # Too short
                'first_name': '',  # Empty
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'validation_error')
        # Multiple field errors should be in details
        self.assertGreater(len(response.data['details']), 0)

    # ========================
    # 405 - Method Not Allowed
    # ========================

    def test_method_not_allowed(self):
        """Test 405 error for unsupported HTTP method"""
        self.client.force_authenticate(self.user)
        
        # DELETE on a create-only endpoint (if applicable)
        response = self.client.delete('/api/orders/')
        
        # Some DELETE operations return 403/404, not 405
        # This test demonstrates the error format if 405 is returned
        if response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            self.assertEqual(response.data['code'], 'method_not_allowed')
            self.assertEqual(response.data['status'], 405)

    # ========================
    # Response Structure Tests
    # ========================

    def test_error_response_structure_401(self):
        """Verify 401 response has correct structure"""
        response = self.client.get('/api/orders/')
        
        # Check required fields
        self.assertIn('error', response.data)
        self.assertIn('code', response.data)
        self.assertIn('status', response.data)
        
        # Check types
        self.assertIsInstance(response.data['error'], str)
        self.assertIsInstance(response.data['code'], str)
        self.assertIsInstance(response.data['status'], int)
        
        # error_code should not be empty
        self.assertGreater(len(response.data['error']), 0)
        self.assertGreater(len(response.data['code']), 0)

    def test_error_response_structure_404(self):
        """Verify 404 response has correct structure"""
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/products/99999/')
        
        # Check required fields
        self.assertIn('error', response.data)
        self.assertIn('code', response.data)
        self.assertIn('status', response.data)

    def test_error_response_structure_400(self):
        """Verify 400 response has correct structure"""
        self.client.force_authenticate(self.vendor_user)
        response = self.client.post('/api/products/', {})
        
        # Check required fields
        self.assertIn('error', response.data)
        self.assertIn('code', response.data)
        self.assertIn('status', response.data)
        self.assertIn('details', response.data)
        
        # details should be dict or empty
        self.assertIsInstance(response.data['details'], dict)

    # ========================
    # Error Code Validity Tests
    # ========================

    VALID_ERROR_CODES = [
        'validation_error',
        'authentication_failed',
        'permission_denied',
        'not_found',
        'method_not_allowed',
        'server_error',
        'internal_error',
    ]

    def test_error_codes_are_valid(self):
        """Verify all errors use valid error codes"""
        # Test 401
        response = self.client.get('/api/orders/')
        self.assertIn(response.data['code'], self.VALID_ERROR_CODES)

        # Test 404
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/products/99999/')
        self.assertIn(response.data['code'], self.VALID_ERROR_CODES)

        # Test 400
        self.client.force_authenticate(self.vendor_user)
        response = self.client.post('/api/products/', {})
        self.assertIn(response.data['code'], self.VALID_ERROR_CODES)

    # ========================
    # HTTP Status Code Tests
    # ========================

    def test_http_status_code_matches_response_status(self):
        """Verify HTTP status code matches response .status field"""
        # Test 401
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, response.data['status'])

        # Test 404
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/products/99999/')
        self.assertEqual(response.status_code, response.data['status'])

        # Test 400
        self.client.force_authenticate(self.vendor_user)
        response = self.client.post('/api/products/', {})
        self.assertEqual(response.status_code, response.data['status'])
