"""
Authentication API module for NodeBB.

Handles user registration, login, and token management.
"""

from __future__ import annotations

from typing import Optional, Dict, Any
import re

from nodebb.exceptions import APIError, ValidationError, NetworkError


class AuthAPI:
    """Handles authentication API endpoints.

    This class provides methods for:
    - User registration
    - User login
    - CSRF token management
    - Session management

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig(base_url="https://forum.example.com")
        >>> client = NodeBBClient(config)
        >>> # Register a new user
        >>> result = client.auth.register("testuser", "password123", "test@example.com")
        >>> # Login to get token
        >>> token_data = client.auth.login("testuser", "password123")
    """

    def __init__(self, http_client, config):
        """Initialize Auth API.

        Args:
            http_client: HTTP client for making requests
            config: NodeBBConfig instance
        """
        self._client = http_client
        self._config = config
        self._csrf_token = None
        self._session_id = None

    def get_csrf_token(self) -> str:
        """Get CSRF token for protected endpoints.

        Retrieves a CSRF token from the API config endpoint.
        The token is cached for subsequent requests.

        Returns:
            CSRF token string

        Raises:
            NetworkError: If request fails

        API Endpoint:
            GET /api/config
        """
        if self._csrf_token:
            return self._csrf_token

        result = self._client.get("/api/config")
        if isinstance(result, dict) and "csrf_token" in result:
            self._csrf_token = result["csrf_token"]
            return self._csrf_token

        # If no csrf_token in config, generate a placeholder
        # Many endpoints work without it if using session-based auth
        return ""

    def register(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        password_confirm: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new user.

        Creates a new user account on the forum.

        Args:
            username: Username (required)
            password: Password (required)
            email: Email address (optional, depending on forum config)
            password_confirm: Password confirmation (defaults to password)
            token: Invitation token (required for invite-only forums)

        Returns:
            Dictionary containing:
                - uid: Created user ID (if registration successful)
                - next: Redirect URL (for interstitials)
                - message: Status message

        Raises:
            ValidationError: If username/password is invalid
            NetworkError: If request fails
            APIError: If registration is disabled or fails

        API Endpoint:
            POST /register
        """
        csrf_token = self.get_csrf_token()

        data = {
            "username": username,
            "password": password,
            "password-confirm": password_confirm or password,
            "csrf_token": csrf_token,
        }

        if email:
            data["email"] = email

        if token:
            data["token"] = token

        # For registration, we need to use form-encoded data
        # and handle CSRF specially
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if csrf_token:
            headers["x-csrf-token"] = csrf_token

        # Make the request directly through http_client
        url = f"{self._config.base_url}/register"
        response = self._client.client.post(
            url,
            data=data,
            headers=headers,
        )

        # Handle the response - check content type first
        if response.status_code >= 400:
            # Error response - try to get more details
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    result = response.json()
                    if isinstance(result, dict) and "status" in result:
                        raise APIError(result.get("status", {}).get("message", "Registration failed"))
                except Exception:
                    pass
            raise APIError(f"Registration failed with status {response.status_code}")

        # Success response
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            # JSON response
            try:
                result = response.json()
                if result.get("next") == "/register/complete":
                    # Registration successful, requires completion
                    return {"next": "/register/complete", "status": "ok", "message": "Registration pending completion"}
                return result
            except Exception as e:
                # If JSON parsing fails, return a generic success
                return {"next": "/", "status": "ok", "message": "Registration successful", "raw_response": str(e)}
        # HTML response or other
        return {"next": "/", "status": "ok", "message": "Registration successful"}

    def login(
        self,
        username: str,
        password: str,
        remember: bool = False,
    ) -> Dict[str, Any]:
        """Login to get user session/token.

        Authenticates a user and returns session information.

        Args:
            username: Username or email
            password: User password
            remember: Whether to remember the login (default: False)

        Returns:
            Dictionary containing:
                - next: Redirect URL after successful login
                - uid: User ID (if available)

        Raises:
            ValidationError: If credentials are invalid
            NetworkError: If request fails

        API Endpoint:
            POST /login
        """
        csrf_token = self.get_csrf_token()

        data = {
            "username": username,
            "password": password,
            "csrf_token": csrf_token,
        }

        if remember:
            data["remember"] = "on"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if csrf_token:
            headers["x-csrf-token"] = csrf_token

        # Make the request directly through http_client
        url = f"{self._config.base_url}/login"
        response = self._client.client.post(
            url,
            data=data,
            headers=headers,
        )

        # Handle the response - check content type first
        if response.status_code >= 400:
            # Error response - try to get more details
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # HTML error response - might contain error message
                text = response.text
                if "[[error:invalid-login-credentials]]" in text:
                    raise ValidationError("Invalid username or password")
            raise ValidationError(f"Login failed with status {response.status_code}")

        # Success response
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            # JSON response
            try:
                return response.json()
            except Exception:
                pass
        # HTML response or other
        return {"next": "/", "status": "ok", "message": "Login successful"}

    def register_complete(self) -> Dict[str, Any]:
        """Complete registration after interstitials.

        Finalizes the registration process after any required
        interstitials (like email verification) are handled.

        Returns:
            Dictionary containing registration completion status

        Raises:
            NetworkError: If request fails

        API Endpoint:
            POST /register/complete
        """
        csrf_token = self.get_csrf_token()

        data = {"csrf_token": csrf_token}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if csrf_token:
            headers["x-csrf-token"] = csrf_token

        url = f"{self._config.base_url}/register/complete"
        response = self._client.client.post(
            url,
            data=data,
            headers=headers,
        )

        # Handle the response
        if response.status_code >= 400:
            raise NetworkError(f"Registration completion failed with status {response.status_code}")

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except Exception:
                pass
        return {"status": "ok", "message": "Registration complete"}

    def logout(self) -> Dict[str, Any]:
        """Logout the current user.

        Ends the current user session.

        Returns:
            Dictionary containing:
                - next: Redirect URL after logout

        Raises:
            NetworkError: If request fails

        API Endpoint:
            POST /logout
        """
        csrf_token = self.get_csrf_token()

        data = {"csrf_token": csrf_token}
        headers = {}
        if csrf_token:
            headers["x-csrf-token"] = csrf_token

        url = f"{self._config.base_url}/logout"
        response = self._client.client.post(
            url,
            data=data,
            headers=headers,
        )

        # Handle the response - check content type first
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            # JSON response
            from nodebb.utils import parse_response
            return parse_response(response.json())
        else:
            # HTML response or other
            if response.status_code >= 400:
                raise APIError(f"Logout failed with status {response.status_code}")
            # Successful logout
            return {"next": "/", "status": "ok", "message": "Logout successful"}

    def get_user_token(self, username: str, password: str) -> str:
        """Get user API token via login.

        This is a convenience method that logs in and attempts
        to extract the user token from the session.

        Note: NodeBB user tokens are typically created via the
        admin panel or user settings. This method establishes
        a session that can be used for cookie-based auth.

        Args:
            username: Username or email
            password: User password

        Returns:
            Session cookie value for cookie-based authentication

        Raises:
            ValidationError: If credentials are invalid
            NetworkError: If request fails
        """
        self.login(username, password)

        # Extract session cookie from the client
        for cookie in self._client.client.cookies:
            if "express.sid" in cookie.name or "nodebb" in cookie.name.lower():
                return cookie.value

        # Return the cookie jar as a string for session management
        return str(self._client.client.cookies)
