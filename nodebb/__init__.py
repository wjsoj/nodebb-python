"""
NodeBB Python Client
~~~~~~~~~~~~~~~~~~

A modern Python client for NodeBB Forum API with OpenAI Function Calling support.

Example:
    >>> from nodebb import NodeBBClient, NodeBBConfig
    >>> config = NodeBBConfig(base_url="https://forum.example.com", token="...")
    >>> client = NodeBBClient(config)
    >>> notifications = client.get_notifications()

:copyright: (c) 2026
:license: MIT
"""

__version__ = "1.0.0"
__author__ = "NodeBB Community"

from nodebb.config import NodeBBConfig
from nodebb.exceptions import (
    NodeBBError,
    AuthenticationError,
    PrivilegeError,
    ResourceNotFoundError,
    RateLimitError,
    ValidationError,
)
from nodebb.client import NodeBBClient
from nodebb.tools import get_tool_definitions, execute_tool

__all__ = [
    # Version info
    "__version__",
    "__author__",
    # Configuration
    "NodeBBConfig",
    # Exceptions
    "NodeBBError",
    "AuthenticationError",
    "PrivilegeError",
    "ResourceNotFoundError",
    "RateLimitError",
    "ValidationError",
    # Main client
    "NodeBBClient",
    # Tools
    "get_tool_definitions",
    "execute_tool",
]
