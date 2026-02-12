"""
Utility functions for NodeBB client.

Provides helper functions used across the client.
"""

from __future__ import annotations

import os
from typing import Optional


def get_content_type(file_path: str) -> str:
    """Get MIME content type for a file based on extension.

    Args:
        file_path: Path to the file

    Returns:
        MIME type string (e.g., 'image/jpeg')

    Examples:
        >>> get_content_type("photo.jpg")
        'image/jpeg'
        >>> get_content_type("document.pdf")
        'application/octet-stream'
    """
    ext = os.path.splitext(file_path)[1].lower()

    types = {
        # Images
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".jpe": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".bmp": "image/bmp",
        ".ico": "image/x-icon",
        # Documents
        ".pdf": "application/pdf",
        ".txt": "text/plain",
        ".html": "text/html",
        ".css": "text/css",
        ".js": "application/javascript",
        ".json": "application/json",
        ".xml": "application/xml",
    }

    return types.get(ext, "application/octet-stream")


def normalize_url(url: str) -> str:
    """Normalize a URL by removing trailing slashes.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL
    """
    return url.rstrip("/")


def build_headers(config) -> dict:
    """Build default HTTP headers for API requests.

    Args:
        config: NodeBBConfig instance

    Returns:
        Dictionary of HTTP headers
    """
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "NodeBB-Python-Client/1.0.0",
    }

    if config.user_token:
        headers["Authorization"] = f"Bearer {config.user_token}"
    elif config.master_token:
        headers["Authorization"] = f"Bearer {config.master_token}"

    return headers


def prepare_request_body(data: Optional[dict], config) -> dict:
    """Prepare request body, adding _uid for master tokens.

    Args:
        data: Original request data
        config: NodeBBConfig instance

    Returns:
        Prepared request body
    """
    if data is None:
        data = {}

    if config.master_token and config.uid is not None:
        data = dict(data)  # Make a copy
        data["_uid"] = config.uid

    return data


def parse_response(response_data: dict) -> dict:
    """Parse API response, handling both read and write API formats.

    Args:
        response_data: Raw JSON response from API

    Returns:
        Parsed response data

    Note:
        Write API returns: {status: {...}, response: {...}}
        Read API returns: {...} directly
    """
    if not isinstance(response_data, dict):
        return response_data

    if "status" in response_data:
        # Write API format
        status = response_data.get("status", {})
        # Check if status is a dict (Write API v3) or string (legacy)
        if isinstance(status, dict):
            if status.get("code") != "ok":
                message = status.get("message", "Unknown error")
                return {"error": message, "status": status}
            return response_data.get("response", {})
        # If status is a string, just return response_data as-is
        return response_data

    # Read API format - return as-is
    return response_data


def extract_error_message(response_data: dict) -> str:
    """Extract error message from API response.

    Args:
        response_data: Raw JSON response from API

    Returns:
        Error message string
    """
    if isinstance(response_data, dict):
        # Check Write API format
        if "status" in response_data:
            status = response_data["status"]
            if "message" in status:
                return status["message"]
        # Check for direct error fields
        if "error" in response_data:
            return str(response_data["error"])
        if "message" in response_data:
            return response_data["message"]
    return "Unknown API error"


def is_success_response(response_data: dict) -> bool:
    """Check if API response indicates success.

    Args:
        response_data: Raw JSON response from API

    Returns:
        True if response indicates success
    """
    if not isinstance(response_data, dict):
        return False

    if "status" in response_data:
        return response_data["status"].get("code") == "ok"

    return True
