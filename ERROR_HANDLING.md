# API Error Handling Documentation 🔥

## Overview

The API implements a **global exception handler** that returns consistent, professional error responses. All errors follow a standardized JSON format that helps frontend developers quickly identify and handle issues.

---

## Error Response Format

All API errors return a standardized JSON response:

```json
{
  "error": "User-friendly error message",
  "code": "error_code_identifier",
  "status": 400,
  "details": {}
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Human-readable error message for the frontend |
| `code` | string | Machine-readable error code for programmatic handling |
| `status` | integer | HTTP status code (for reference in response body) |
| `details` | object | (Optional) Additional context, usually field-level validation errors |

---

## HTTP Status Codes & Error Codes

### 400 - Bad Request (Validation Errors)

**Code:** `validation_error`

Returned when request data fails validation.

**Example 1: Missing Required Field**
```json
{
  "error": "Email: This field may not be blank.",
  "code": "validation_error",
  "status": 400,
  "details": {
    "email": "This field may not be blank."
  }
}
```

**Example 2: Invalid Data Type**
```json
{
  "error": "Quantity: A valid integer is required.",
  "code": "validation_error",
  "status": 400,
  "details": {
    "quantity": "A valid integer is required."
  }
}
```

**Example 3: Multiple Validation Errors**
```json
{
  "error": "Username: Ensure this field has at most 150 characters.",
  "code": "validation_error",
  "status": 400,
  "details": {
    "username": "Ensure this field has at most 150 characters.",
    "password": "This field may not be blank.",
    "email": "Enter a valid email address."
  }
}
```

---

### 401 - Unauthorized (Authentication Failed)

**Code:** `authentication_failed`

Returned when request lacks valid authentication credentials.

**Example: Missing or Invalid Token**
```json
{
  "error": "Authentication failed",
  "code": "authentication_failed",
  "status": 401
}
```

**Scenario:**
- Missing Authorization header
- Invalid JWT token format
- Expired JWT token
- Invalid token signature

---

### 403 - Forbidden (Permission Denied)

**Code:** `permission_denied`

Returned when authenticated user lacks permission to access resource.

**Example 1: Insufficient Permissions**
```json
{
  "error": "Only vendors can create products",
  "code": "permission_denied",
  "status": 403
}
```

**Example 2: Not Resource Owner**
```json
{
  "error": "You can only modify your own profile",
  "code": "permission_denied",
  "status": 403
}
```

**Scenario:**
- User is not a vendor trying to create product
- Customer trying to access vendor dashboard
- User trying to modify another user's order
- Insufficient role/permission level

---

### 404 - Not Found

**Code:** `not_found`

Returned when requested resource doesn't exist.

**Example 1: Product Not Found**
```json
{
  "error": "Product not found",
  "code": "not_found",
  "status": 404
}
```

**Example 2: Order Not Found**
```json
{
  "error": "Order not found",
  "code": "not_found",
  "status": 404
}
```

**Scenario:**
- Product ID doesn't exist
- Order ID doesn't exist (or doesn't belong to user)
- Chat room doesn't exist
- User profile doesn't exist

---

### 405 - Method Not Allowed

**Code:** `method_not_allowed`

Returned when HTTP method is not supported on endpoint.

**Example:**
```json
{
  "error": "Method not allowed",
  "code": "method_not_allowed",
  "status": 405
}
```

**Scenario:**
- POST request to read-only endpoint
- PUT to endpoint that only supports GET/POST
- DELETE on non-deletable resource

---

### 500 - Internal Server Error

**Code:** `server_error` or `internal_error`

Returned when unexpected server error occurs.

**Example:**
```json
{
  "error": "Internal server error",
  "code": "server_error",
  "status": 500
}
```

---

## Common Error Scenarios

### Authentication Errors

**Scenario 1: Missing Authorization Header**
```bash
$ curl -X GET http://localhost:8000/api/orders/
```

**Response:**
```json
{
  "error": "Authentication failed",
  "code": "authentication_failed",
  "status": 401
}
```

**Solution:** Include Authorization header with valid JWT token
```bash
$ curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

### Validation Errors

**Scenario 2: Create Order with Invalid Data**
```bash
$ curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"invalid_field": "value"}'
```

**Response:**
```json
{
  "error": "Validation failed",
  "code": "validation_error",
  "status": 400,
  "details": {}
}
```

---

### Permission Errors

**Scenario 3: Customer Trying to Create Product**
```bash
$ curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer CUSTOMER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Product", ...}'
```

**Response:**
```json
{
  "error": "Only vendors can create products",
  "code": "permission_denied",
  "status": 403
}
```

**Solution:** Use vendor account or request vendor status

---

### Not Found Errors

**Scenario 4: Access Non-Existent Product**
```bash
$ curl -X GET http://localhost:8000/api/products/99999/ \
  -H "Authorization: Bearer TOKEN"
```

**Response:**
```json
{
  "error": "Product not found",
  "code": "not_found",
  "status": 404
}
```

---

## Frontend Error Handling Examples

### JavaScript/React

```javascript
// Fetch API with error handling
fetch('/api/products/', {
  headers: {
    'Authorization': `Bearer ${token}`,
  }
})
.then(response => {
  if (!response.ok) {
    return response.json().then(data => {
      throw new Error(data.error);
    });
  }
  return response.json();
})
.catch(error => {
  // Display error to user
  showNotification(error.message, 'error');
  console.error(`[${error.code}] ${error.error}`);
});

// Handle specific error codes
async function getProduct(id) {
  try {
    const response = await fetch(`/api/products/${id}/`);
    const data = await response.json();
    
    if (!response.ok) {
      switch (data.code) {
        case 'not_found':
          showDialog('Product not found');
          break;
        case 'authentication_failed':
          redirectToLogin();
          break;
        case 'permission_denied':
          showDialog('You don\'t have permission to access this');
          break;
        case 'validation_error':
          displayFormErrors(data.details);
          break;
        default:
          showDialog(`Error: ${data.error}`);
      }
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('Network error:', error);
    showDialog('Network error occurred');
  }
}
```

### Vue.js Example

```vue
<script>
export default {
  methods: {
    async loadProduct(id) {
      try {
        const response = await this.$http.get(`/api/products/${id}/`);
        this.product = response.data;
      } catch (error) {
        const { code, error: message } = error.response?.data || {};
        
        this.handleError(code, message);
      }
    },
    
    handleError(code, message) {
      const errorMap = {
        'not_found': 'Product not found',
        'authentication_failed': 'Please login again',
        'permission_denied': 'You don\'t have permission',
        'validation_error': 'Please check your input',
      };
      
      this.$toast.error(errorMap[code] || message);
    }
  }
}
</script>
```

---

## Implementation Details

### File Location

**Exception Handler:** `config/exceptions.py`

**Settings Configuration:** `config/settings/base.py`

```python
REST_FRAMEWORK = {
    # ... other settings ...
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}
```

### How It Works

1. **DRF Exceptions Caught First**
   - ValidationError (400) - Field validation failures
   - NotFound (404) - Resource doesn't exist
   - PermissionDenied (403) - User lacks permission
   - AuthenticationFailed (401) - Invalid credentials
   - NotAuthenticated (401) - No credentials provided
   - MethodNotAllowed (405) - Unsupported HTTP method

2. **Django Exceptions**
   - `Http404` → 404 not_found error
   - `PermissionDenied` → 403 permission_denied error
   - `ValidationError` → 400 validation_error

3. **Unhandled Exceptions**
   - Logged to console/file
   - Return 500 internal_error response
   - Safe error message (no sensitive info leaked)

---

## Testing Error Responses

### Test Cases Included

```bash
# Run all tests
python manage.py test

# Test specific failing scenario
python manage.py test chat.tests.ChatAPITestCase.test_room_list_requires_auth

# Test with coverage
coverage run --source='.' manage.py test
coverage report
```

### Manual Testing

```bash
# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver

# Test 404 error
curl http://localhost:8000/api/products/99999/

# Test 401 error
curl http://localhost:8000/api/orders/

# Test 403 error
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Test 400 validation error
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid"}'
```

---

## Error Code Reference

| HTTP Status | Code | Meaning | Action |
|---|---|---|---|
| 400 | `validation_error` | Invalid request data | Check request format, fix fields |
| 401 | `authentication_failed` | Invalid/missing credentials | Reauthenticate, get new token |
| 403 | `permission_denied` | Insufficient permissions | Request permission, use different account |
| 404 | `not_found` | Resource doesn't exist | Check ID, use correct endpoint |
| 405 | `method_not_allowed` | Wrong HTTP method | Use correct HTTP verb (GET/POST/etc) |
| 500 | `server_error` | Unexpected error | Retry, contact support, check logs |

---

## Best Practices

### For Frontend Developers

1. **Always check the error response**
   ```javascript
   if (response.ok) { /* success */ }
   else { /* handle error.code */ }
   ```

2. **Use error.code for programmatic handling**
   ```javascript
   // Good - programmatic
   if (error.code === 'not_found') { redirect('/notfound'); }
   
   // Avoid - string matching on message
   if (error.message.includes('not found')) { ... }
   ```

3. **Display error.error to users**
   ```javascript
   // Always show error.error, not error.details
   toast.error(error.error);
   ```

4. **Use error.details for form validation**
   ```javascript
   // error.details contains field: message pairs
   Object.entries(error.details).forEach(([field, message]) => {
     form.setFieldError(field, message);
   });
   ```

### For Backend Developers

1. **Keep error messages user-friendly**
   ```python
   # Good
   raise ValidationError("Email already exists")
   
   # Bad
   raise ValidationError("Unique constraint violation on users_email")
   ```

2. **Use appropriate HTTP status codes**
   ```python
   # Good
   from rest_framework.exceptions import NotFound
   raise NotFound("Product not found")
   
   # Bad
   return Response({"error": "Not found"}, status=500)
   ```

3. **Don't expose sensitive information**
   ```python
   # Bad - exposes database details
   except Exception as e:
       return Response({"error": str(e)})
   
   # Good - safe generic message
   except Exception as e:
       logger.error(str(e))
       return Response({"error": "An error occurred"}, status=500)
   ```

---

## Version History

- **v1.0.0** (2025-01-17)
  - Global exception handler implemented
  - Standardized error response format
  - Covered all HTTP status codes (400, 401, 403, 404, 405, 500)
  - Frontend integration examples provided
  - Comprehensive documentation created

---

**Last Updated:** 2025-01-17  
**Status:** ✅ PRODUCTION READY
