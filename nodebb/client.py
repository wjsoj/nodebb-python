"""
Main client module for NodeBB.

Provides the NodeBBClient class that coordinates all API operations.
"""

from __future__ import annotations

import httpx
import json
from typing import Optional, Dict, Any

from nodebb.config import NodeBBConfig
from nodebb.exceptions import (
    NodeBBError,
    AuthenticationError,
    PrivilegeError,
    ResourceNotFoundError,
    RateLimitError,
    ValidationError,
    APIError,
    NetworkError,
)
from nodebb.api.read import ReadAPI
from nodebb.api.write import WriteAPI
from nodebb.api.chat import ChatAPI
from nodebb.api.upload import UploadAPI
from nodebb.api.auth import AuthAPI
from nodebb.utils import build_headers, prepare_request_body, parse_response, is_success_response


class HTTPClient:
    """Internal HTTP client wrapper.

    Wraps httpx.Client with NodeBB-specific request handling.
    """

    def __init__(self, config: NodeBBConfig):
        """Initialize HTTP client.

        Args:
            config: NodeBBConfig instance
        """
        self.config = config
        self.client = httpx.Client(
            timeout=config.timeout,
            verify=config.verify_ssl,
            headers=build_headers(config),
        )
        self.base_url = config.base_url

    def _make_url(self, endpoint: str) -> str:
        """Build full URL from endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Full URL
        """
        return f"{self.base_url}{endpoint}"

    def _handle_response(self, response: httpx.Response, endpoint: str) -> Any:
        """Handle HTTP response, extracting data and checking errors.

        Args:
            response: HTTP response object
            endpoint: API endpoint that was called

        Returns:
            Parsed response data

        Raises:
            AuthenticationError: For 401 status
            PrivilegeError: For 403 status
            ResourceNotFoundError: For 404 status
            RateLimitError: For 429 status
            APIError: For other 4xx/5xx errors
            NetworkError: For connection errors
        """
        try:
            # Check for HTTP status errors first
            if response.status_code == 401:
                raise AuthenticationError("Invalid or missing authentication token")
            elif response.status_code == 403:
                raise PrivilegeError("Insufficient privileges for this operation")
            elif response.status_code == 404:
                raise ResourceNotFoundError(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code >= 400:
                # Parse error response
                try:
                    result = response.json()
                    # Check Write API format
                    if isinstance(result, dict) and "status" in result:
                        status = result["status"]
                        if status.get("code") == "bad-params":
                            raise ValidationError(
                                "Invalid parameters",
                                errors=status.get("params", []),
                            )
                        raise APIError(
                            status.get("message", "API error"),
                            status_code=response.status_code,
                        )
                except Exception:
                    raise APIError(
                        f"API error ({response.status_code})",
                        status_code=response.status_code,
                    )

            # Parse JSON response
            result = response.json()
            return parse_response(result)

        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {e}")
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP error: {e}")
        except httpx.RequestError as e:
            raise NetworkError(f"Request error: {e}")

    def get(self, endpoint: str, params: Optional[dict] = None) -> Any:
        """Make GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Parsed response data
        """
        url = self._make_url(endpoint)
        response = self.client.get(url, params=params)
        return self._handle_response(response, endpoint)

    def post(
        self,
        endpoint: str,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
    ) -> Any:
        """Make POST request.

        Args:
            endpoint: API endpoint path
            data: Request body data
            files: Files to upload

        Returns:
            Parsed response data
        """
        url = self._make_url(endpoint)
        body = prepare_request_body(data, self.config) if not files else None
        kwargs = {"json": body} if not files else {"files": files}
        response = self.client.post(url, **kwargs)
        return self._handle_response(response, endpoint)

    def put(self, endpoint: str, data: Optional[dict] = None) -> Any:
        """Make PUT request.

        Args:
            endpoint: API endpoint path
            data: Request body data

        Returns:
            Parsed response data
        """
        url = self._make_url(endpoint)
        body = prepare_request_body(data, self.config)
        response = self.client.put(url, json=body)
        return self._handle_response(response, endpoint)

    def delete(self, endpoint: str, data: Optional[dict] = None) -> Any:
        """Make DELETE request.

        Args:
            endpoint: API endpoint path
            data: Request body data (for DELETE with body)

        Returns:
            Parsed response data
        """
        url = self._make_url(endpoint)
        body = prepare_request_body(data, self.config)
        response = self.client.request("DELETE", url, json=body)
        return self._handle_response(response, endpoint)

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close client."""
        self.close()


class NodeBBClient:
    """Main client for interacting with NodeBB API.

    This client provides a high-level interface to all NodeBB API endpoints.
    Use it as a context manager for automatic cleanup:

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig.from_env()
        >>> with NodeBBClient(config) as client:
        ...     notifications = client.read.get_notifications()
        ...     client.write.create_topic(cid=1, title="Hi", content="Hello")

    The client has sub-APIs organized by function:
        - client.read: ReadAPI for GET endpoints
        - client.write: WriteAPI for content modification
        - client.chat: ChatAPI for messaging
        - client.upload: UploadAPI for file uploads
        - client.auth: AuthAPI for authentication
    """

    def __init__(self, config: NodeBBConfig):
        """Initialize NodeBB client.

        Args:
            config: NodeBBConfig instance with connection settings

        Raises:
            ConfigurationError: If config validation fails
        """
        config.validate()
        self.config = config
        self._http = HTTPClient(config)

        # Initialize API modules
        self.read = ReadAPI(self._http, config)
        self.write = WriteAPI(self._http, config)
        self.chat = ChatAPI(self._http, config)
        self.upload = UploadAPI(self._http, config)
        self.auth = AuthAPI(self._http, config)

        # Auto-login if username and password are provided
        if config.username and config.password:
            try:
                self.login(username=config.username, password=config.password)
            except Exception as e:
                # Don't fail initialization, but log the error
                import warnings
                warnings.warn(f"Auto-login failed: {e}", RuntimeWarning)

    def close(self):
        """Close the client and release resources."""
        self._http.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close client."""
        self.close()

    # ========================================================================
    # Convenience Methods - Direct API Access
    # ========================================================================

    # Read API shortcuts
    def get_notifications(self, filter: str = "", page: int = 1):
        return self.read.get_notifications(filter=filter, page=page)

    def get_unread_count(self) -> int:
        return self.read.get_unread_count()

    def get_unread_topics(
        self,
        start: Optional[int] = None,
        per_page: Optional[int] = None,
        filter: str = "",
    ):
        return self.read.get_unread_topics(start=start, per_page=per_page, filter=filter)

    def get_recent_posts(self, term: str = "all", page: Optional[int] = None):
        return self.read.get_recent_posts(term=term, page=page)

    def get_topic(self, tid: int, slug: str = "", post_index: Optional[int] = None):
        return self.read.get_topic(tid=tid, slug=slug, post_index=post_index)

    def get_categories(self):
        return self.read.get_categories()

    def get_category(self, cid: int, slug: str = "", topic_index: Optional[int] = None):
        return self.read.get_category(cid=cid, slug=slug, topic_index=topic_index)

    def get_user(self, uid: int):
        return self.read.get_user(uid=uid)

    def get_user_by_username(self, userslug: str):
        return self.read.get_user_by_username(userslug=userslug)

    def search_users(self, query: str = "", section: str = "joindate", page: Optional[int] = None):
        return self.read.search_users(query=query, section=section, page=page)

    def get_config(self):
        return self.read.get_config()

    def get_post(self, pid: int):
        return self.read.get_post(pid=pid)

    # Write API shortcuts
    def create_topic(self, cid: int, title: str, content: str, tags: Optional[list] = None, timestamp: Optional[int] = None):
        return self.write.create_topic(cid=cid, title=title, content=content, tags=tags, timestamp=timestamp)

    def create_reply(self, tid: int, content: str, to_pid: Optional[int] = None):
        return self.write.create_reply(tid=tid, content=content, to_pid=to_pid)

    def edit_post(self, pid: int, content: str, title: Optional[str] = None):
        return self.write.edit_post(pid=pid, content=content, title=title)

    def delete_post(self, pid: int):
        return self.write.delete_post(pid=pid)

    def delete_topic(self, tid: int):
        return self.write.delete_topic(tid=tid)

    def vote_post(self, pid: int, delta: int = 1):
        return self.write.vote_post(pid=pid, delta=delta)

    def unvote_post(self, pid: int):
        return self.write.unvote_post(pid=pid)

    def bookmark_post(self, pid: int):
        return self.write.bookmark_post(pid=pid)

    def unbookmark_post(self, pid: int):
        return self.write.unbookmark_post(pid=pid)

    def follow_topic(self, tid: int):
        return self.write.follow_topic(tid=tid)

    def unfollow_topic(self, tid: int):
        return self.write.unfollow_topic(tid=tid)

    def mark_topic_read(self, tid: int):
        return self.write.mark_topic_read(tid=tid)

    def mark_topic_unread(self, tid: int):
        return self.write.mark_topic_unread(tid=tid)

    # Chat API shortcuts
    def get_chats(self, start: Optional[int] = None, per_page: Optional[int] = None):
        return self.chat.get_rooms(start=start, per_page=per_page)

    def get_or_create_chat_with_user(self, uid: int):
        """获取或创建与指定用户的聊天室"""
        return self.chat.get_or_create_room_with_user(uid=uid)

    def create_chat_room(self, uids: list):
        return self.chat.create_room(uids=uids)

    def send_chat_message(self, room_id: int, message: str, to_mid: str = ""):
        return self.chat.send_message(room_id=room_id, message=message, to_mid=to_mid)

    def get_chat_messages(self, room_id: int, start: Optional[int] = None, count: Optional[int] = None):
        return self.chat.get_messages(room_id=room_id, start=start, count=count)

    def get_chat_room_detail(self, room_id: int):
        return self.chat.get_room_detail(room_id=room_id)

    def add_users_to_chat(self, room_id: int, uids: list):
        return self.chat.add_users(room_id=room_id, uids=uids)

    def leave_chat_room(self, room_id: int):
        return self.chat.leave_room(room_id=room_id)

    # Upload API shortcuts
    def upload_image(self, file_path: str):
        return self.upload.image(file_path=file_path)

    def upload_file(self, file_path: str):
        return self.upload.post_file(file_path=file_path)

    # Auth API shortcuts
    def register(self, username: str, password: str, email: Optional[str] = None, password_confirm: Optional[str] = None, token: Optional[str] = None):
        return self.auth.register(username=username, password=password, email=email, password_confirm=password_confirm, token=token)

    def login(self, username: str, password: str, remember: bool = False):
        return self.auth.login(username=username, password=password, remember=remember)

    def logout(self):
        return self.auth.logout()

    def get_user_token(self, username: str, password: str) -> str:
        return self.auth.get_user_token(username=username, password=password)
