"""
Configuration module for NodeBB client.

Provides configuration classes and factory methods for creating client instances.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Load .env from current directory or python_client directory
    env_path = Path('.env')
    if not env_path.exists():
        env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed, skip
    pass


@dataclass
class NodeBBConfig:
    """Configuration for NodeBB API client.

    Attributes:
        base_url: The base URL of the NodeBB forum (e.g., 'https://forum.example.com')
        username: Username for login authentication
        password: Password for login authentication
        user_token: User-specific bearer token for API authentication
        master_token: Master bearer token for API authentication (requires _uid in requests)
        timeout: Request timeout in seconds
        verify_ssl: Whether to verify SSL certificates
        uid: User ID (required when using master_token)
    """

    base_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    user_token: Optional[str] = None
    master_token: Optional[str] = None
    timeout: int = 30
    verify_ssl: bool = True
    uid: Optional[int] = None

    def __post_init__(self):
        """Normalize the base URL after initialization."""
        self.base_url = self.base_url.rstrip("/")

    @property
    def is_authenticated(self) -> bool:
        """Check if authentication credentials are configured."""
        return bool(self.user_token or (self.master_token and self.uid))

    @property
    def auth_type(self) -> str:
        """Get the authentication type being used."""
        if self.master_token:
            return "master"
        if self.user_token:
            return "user"
        return "none"

    @classmethod
    def from_env(cls) -> "NodeBBConfig":
        """Create configuration from environment variables.

        Environment Variables:
            NODEBB_BASE_URL: Base URL of the forum (required)
            NODEBB_USERNAME: Username for login authentication
            NODEBB_PASSWORD: Password for login authentication
            NODEBB_USER_TOKEN: User bearer token
            NODEBB_MASTER_TOKEN: Master bearer token
            NODEBB_UID: User ID (required when using master token)
            NODEBB_TIMEOUT: Request timeout in seconds (default: 30)
            NODEBB_VERIFY_SSL: Whether to verify SSL (default: true)

        Returns:
            NodeBBConfig instance with values from environment

        Raises:
            ValueError: If NODEBB_BASE_URL is not set
        """
        base_url = os.getenv("NODEBB_BASE_URL", "")
        if not base_url:
            raise ValueError(
                "NODEBB_BASE_URL environment variable is required. "
                "Set it to your NodeBB forum URL."
            )

        return cls(
            base_url=base_url,
            username=os.getenv("NODEBB_USERNAME"),
            password=os.getenv("NODEBB_PASSWORD"),
            user_token=os.getenv("NODEBB_USER_TOKEN"),
            master_token=os.getenv("NODEBB_MASTER_TOKEN"),
            uid=int(os.getenv("NODEBB_UID")) if os.getenv("NODEBB_UID") else None,
            timeout=int(os.getenv("NODEBB_TIMEOUT", "30")),
            verify_ssl=os.getenv("NODEBB_VERIFY_SSL", "true").lower() == "true",
        )

    @classmethod
    def for_user_token(cls, base_url: str, token: str, **kwargs) -> "NodeBBConfig":
        """Create config with user token.

        Args:
            base_url: Forum base URL
            token: User bearer token
            **kwargs: Additional config options

        Returns:
            NodeBBConfig instance
        """
        return cls(base_url=base_url, user_token=token, **kwargs)

    @classmethod
    def for_master_token(
        cls, base_url: str, token: str, uid: int, **kwargs
    ) -> "NodeBBConfig":
        """Create config with master token.

        Args:
            base_url: Forum base URL
            token: Master bearer token
            uid: User ID to act as
            **kwargs: Additional config options

        Returns:
            NodeBBConfig instance
        """
        return cls(base_url=base_url, master_token=token, uid=uid, **kwargs)

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.base_url:
            raise ValueError("base_url is required")

        if self.master_token and self.uid is None:
            raise ValueError("uid is required when using master_token")

        if not self.user_token and not self.master_token:
            # Config without auth is valid for read-only endpoints
            pass
