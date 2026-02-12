"""
Upload API module for NodeBB.

Handles file upload operations.
"""

from __future__ import annotations

import os
from typing import Dict, Any

from nodebb.utils import get_content_type


class UploadAPI:
    """Handles file upload endpoints.

    This class provides methods for uploading files:
    - Images for use in posts
    - Other attachments

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig.for_user_token("https://forum.example.com", "token")
        >>> client = NodeBBClient(config)
        >>> result = client.upload.image("/path/to/image.png")
    """

    def __init__(self, http_client, config):
        """Initialize Upload API.

        Args:
            http_client: HTTP client for making requests
            config: NodeBBConfig instance
        """
        self._client = http_client
        self._config = config

    def image(self, file_path: str) -> Dict[str, Any]:
        """Upload an image.

        Uploads an image file that can be embedded in posts.

        Args:
            file_path: Path to the image file (required)

        Returns:
            Dictionary containing:
                - url: URL of uploaded image
                - path: File path in uploads folder
                - name: Uploaded filename

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If file is not a valid image
            NetworkError: If upload fails

        Supported Formats:
            jpg, jpeg, png, gif, webp, svg, bmp, ico

        API Endpoint:
            POST /api/post/upload

        Example:
            After upload, use the returned URL in post content:

            >>> result = client.upload.image("/path/to/photo.jpg")
            >>> image_url = result["url"]
            >>> client.create_topic(
            ...     cid=1,
            ...     title="Photo post",
            ...     content=f"![image]({image_url})"
            ... )
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        # Prepare file for upload
        filename = os.path.basename(file_path)
        content_type = get_content_type(file_path)

        # Validate it's an image
        if not content_type.startswith("image/"):
            raise ValueError(
                f"Invalid file type: {content_type}. "
                "Only images are supported."
            )

        with open(file_path, "rb") as f:
            files = {"files[]": (filename, f.read(), content_type)}
            return self._client.post("/api/post/upload", files=files)

    def post_file(self, file_path: str) -> Dict[str, Any]:
        """Upload a file as post attachment.

        Uploads a file for use in forum posts.

        Args:
            file_path: Path to the file (required)

        Returns:
            Dictionary containing:
                - url: URL of uploaded file
                - path: File path in uploads folder
                - name: Uploaded filename

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If file type is not allowed
            FileNotFoundError: If file doesn't exist

        API Endpoint:
            POST /api/post/upload

        Note:
            This method can upload any file type, but administrators
            may configure allowed extensions.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")

        filename = os.path.basename(file_path)
        content_type = get_content_type(file_path)

        with open(file_path, "rb") as f:
            files = {"files[]": (filename, f.read(), content_type)}
            return self._client.post("/api/post/upload", files=files)

    def get_csrf_token(self) -> str:
        """Get CSRF token for form uploads.

        Some upload scenarios may require a CSRF token for security.

        Returns:
            CSRF token string

        Note:
            Most API calls use Bearer authentication and don't need this.
            This is primarily for legacy form-based uploads.
        """
        result = self._client.get("/api/config")
        # CSRF token is often included in config
        if isinstance(result, dict):
            return result.get("csrf_token", "")
        return ""
