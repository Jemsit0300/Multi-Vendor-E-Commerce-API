from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError as DjangoValidationError


def custom_exception_handler(exc, context):
    """
    Custom exception handler for consistent error responses across the API.
    
    Format:
    {
        "error": "Error message",
        "code": "error_code",
        "status": 400,
        "details": {}  # Optional: validation errors or additional context
    }
    """
    
    # Call the default exception handler first
    response = exception_handler(exc, context)

    # Handle DRF exceptions
    if response is not None:
        # Validation errors (400)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            if isinstance(response.data, dict):
                # Extract first error message for simple "error" field
                error_msg = "Validation failed"
                details = {}
                
                for field, messages in response.data.items():
                    if isinstance(messages, list) and messages:
                        error_msg = f"{field.replace('_', ' ').title()}: {messages[0]}"
                        details[field] = messages[0] if isinstance(messages[0], str) else str(messages[0])
                    else:
                        details[field] = str(messages)
                
                return Response(
                    {
                        "error": error_msg,
                        "code": "validation_error",
                        "status": status.HTTP_400_BAD_REQUEST,
                        "details": details
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Not found (404)
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            return Response(
                {
                    "error": response.data.get('detail', 'Resource not found'),
                    "code": "not_found",
                    "status": status.HTTP_404_NOT_FOUND,
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Permission denied (403)
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            return Response(
                {
                    "error": response.data.get('detail', 'Permission denied'),
                    "code": "permission_denied",
                    "status": status.HTTP_403_FORBIDDEN,
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Unauthorized (401)
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            return Response(
                {
                    "error": response.data.get('detail', 'Authentication failed'),
                    "code": "authentication_failed",
                    "status": status.HTTP_401_UNAUTHORIZED,
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Method not allowed (405)
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            return Response(
                {
                    "error": "Method not allowed",
                    "code": "method_not_allowed",
                    "status": status.HTTP_405_METHOD_NOT_ALLOWED,
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        # Server error (500)
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            return Response(
                {
                    "error": "Internal server error",
                    "code": "server_error",
                    "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # For other errors, format the response
        else:
            return Response(
                {
                    "error": str(response.data.get('detail', 'An error occurred')),
                    "code": "error",
                    "status": response.status_code,
                },
                status=response.status_code
            )

    # Handle Django exceptions that DRF doesn't catch
    elif isinstance(exc, Http404):
        return Response(
            {
                "error": "Resource not found",
                "code": "not_found",
                "status": status.HTTP_404_NOT_FOUND,
            },
            status=status.HTTP_404_NOT_FOUND
        )

    elif isinstance(exc, PermissionDenied):
        return Response(
            {
                "error": str(exc.detail) if hasattr(exc, 'detail') else "Permission denied",
                "code": "permission_denied",
                "status": status.HTTP_403_FORBIDDEN,
            },
            status=status.HTTP_403_FORBIDDEN
        )

    elif isinstance(exc, DjangoValidationError):
        return Response(
            {
                "error": str(exc.message) if hasattr(exc, 'message') else str(exc),
                "code": "validation_error",
                "status": status.HTTP_400_BAD_REQUEST,
                "details": exc.params if hasattr(exc, 'params') else {}
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Unhandled exceptions - log and return 500
    return Response(
        {
            "error": "An unexpected error occurred",
            "code": "internal_error",
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
