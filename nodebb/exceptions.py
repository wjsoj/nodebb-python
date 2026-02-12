"""
Exception classes for NodeBB client.

Provides a hierarchy of exceptions for different error scenarios.
"""

from __future__ import annotations

from typing import Optional, Any


class NodeBBError(Exception):
    """Base exception for all NodeBB errors.

    All other exceptions inherit from this class, allowing catch-all error handling:

        try:
            client.get_notifications()
        except NodeBBError as e:
            print(f"NodeBB error: {e}")
    """

    def __init__(self, message: str, response_data: Optional[dict] = None):
        """Initialize exception with message and optional response data.

        Args:
            message: Error message
            response_data: Raw response data from API (if available)
        """
        self.message = message
        self.response_data = response_data
        super().__init__(message)

    def __str__(self) -> str:
        """String representation includes response data if available."""
        if self.response_data:
            return f"{self.message} | Response: {self.response_data}"
        return self.message


class AuthenticationError(NodeBBError):
    """Raised when authentication fails or credentials are invalid.

    This typically occurs when:
    - No authentication token is provided for protected endpoints
    - The provided token has expired or been revoked
    - Invalid credentials are used

    Example:
        >>> try:
        ...     client.create_topic(cid=1, title="Test", content="...")
        ... except AuthenticationError:
        ...     print("Please check your API token")
    """

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)


class PrivilegeError(NodeBBError):
    """Raised when user lacks required privileges for an operation.

    This occurs when the authenticated user doesn't have permission to:
    - Post in a category
    - Edit/delete content
    - Access admin-only endpoints
    - Perform moderator actions

    Example:
        >>> try:
        ...     client.delete_post(pid=123)
        ... except PrivilegeError as e:
        ...     print(f"Insufficient permissions: {e}")
    """

    def __init__(self, message: str = "Insufficient privileges") -> None:
        super().__init__(message)


class ResourceNotFoundError(NodeBBError):
    """Raised when a requested resource is not found.

    This occurs when:
    - Topic/post/user ID doesn't exist
    - Category has been deleted
    - Invalid slug/path is requested

    Example:
        >>> try:
        ...     client.get_topic(tid=99999)
        ... except ResourceNotFoundError:
        ...     print("Topic not found")
    """

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class RateLimitError(NodeBBError):
    """Raised when API rate limit is exceeded.

    NodeBB may limit API requests to prevent abuse.
    Implement exponential backoff for retries:

        import time
        try:
            client.get_notifications()
        except RateLimitError:
            time.sleep(60)  # Wait 1 minute
            client.get_notifications()
    """

    def __init__(
        self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None
    ) -> None:
        """Initialize with optional retry-after duration.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (if provided by API)
        """
        self.retry_after = retry_after
        super().__init__(message)


class ValidationError(NodeBBError):
    """Raised when request validation fails.

    This occurs when:
    - Required parameters are missing
    - Parameter values are invalid
    - Data format is incorrect

    Example:
        >>> try:
        ...     client.create_topic(cid=1, title="", content="...")
        ... except ValidationError as e:
        ...     print(f"Invalid input: {e}")
    """

    def __init__(self, message: str = "Validation failed", errors: Optional[list] = None) -> None:
        """Initialize with optional list of validation errors.

        Args:
            message: Error message
            errors: List of specific validation errors from API
        """
        self.errors = errors or []
        super().__init__(message)


class APIError(NodeBBError):
    """Generic API error for unhandled server responses.

    This is raised for:
    - Server errors (5xx)
    - Malformed responses
    - Unexpected response structures

    Example:
        >>> try:
        ...     client.get_notifications()
        ... except APIError as e:
        ...     print(f"API error: {e}")
    """

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize with optional HTTP status code.

        Args:
            message: Error message
            status_code: HTTP status code (if available)
        """
        self.status_code = status_code
        super().__init__(message)


class NetworkError(NodeBBError):
    """Raised when network-related errors occur.

    This includes:
    - Connection timeouts
    - DNS resolution failures
    - SSL certificate errors
    - Connection refused

    Example:
        >>> try:
        ...     client.get_notifications()
        ... except NetworkError as e:
        ...     print(f"Network error: {e}")
    """

    def __init__(self, message: str = "Network error") -> None:
        super().__init__(message)


class ConfigurationError(NodeBBError):
    """Raised when client configuration is invalid.

    This occurs when:
    - Required configuration values are missing
    - Invalid configuration combinations (e.g., master token without uid)
    - Invalid URL format

    Example:
        >>> try:
        ...     config = NodeBBConfig(base_url="", token="...")
        ...     config.validate()
        ... except ConfigurationError as e:
        ...     print(f"Config error: {e}")
    """

    def __init__(self, message: str = "Invalid configuration") -> None:
        super().__init__(message)
