"""
Chat API module for NodeBB.

Handles private messaging and chat room operations.
All endpoints require authentication.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List


class ChatAPI:
    """Handles chat/messaging API endpoints.

    This class provides methods for:
    - Listing chat rooms
    - Creating chat rooms
    - Sending messages
    - Retrieving chat history

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig.for_user_token("https://forum.example.com", "token")
        >>> client = NodeBBClient(config)
        >>> rooms = client.chat.get_rooms()
    """

    def __init__(self, http_client, config):
        """Initialize Chat API.

        Args:
            http_client: HTTP client for making requests
            config: NodeBBConfig instance
        """
        self._client = http_client
        self._config = config

    def get_rooms(
        self,
        start: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get list of chat rooms.

        Retrieves chat rooms the user is a member of.

        Args:
            start: Start index for pagination (default: 0)
            perPage: Number of rooms per page (default: forum setting)

        Returns:
            Dictionary containing:
                - rooms: Array of chat room objects
                - Each room has: roomId, users, lastUser, etc.
                - unread: Whether room has unread messages
                - teaser: Latest message preview

        Raises:
            AuthenticationError: If not authenticated
            NetworkError: If network request fails

        API Endpoint:
            GET /api/v3/chats/
        """
        params = {}
        if start is not None:
            params["start"] = start
        if per_page is not None:
            params["perPage"] = per_page

        return self._client.get("/api/v3/chats/", params=params)

    def create_room(self, uids: List[int]) -> Dict[str, Any]:
        """Create a new chat room.

        Creates a new chat room with specified users.

        Args:
            uids: List of user IDs to add to the chat (required)
                    Note: Creating user is automatically included

        Returns:
            Dictionary containing:
                - roomId: Created room ID
                - users: Array of users in room
                - owner: User ID of room owner
                - timestamp: Creation timestamp

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If uids is empty or invalid

        API Endpoint:
            POST /api/v3/chats/
        """
        return self._client.post("/api/v3/chats/", data={"uids": uids})

    def get_or_create_room_with_user(self, uid: int) -> Dict[str, Any]:
        """获取或创建与指定用户的聊天室。

        如果与该用户的聊天室已存在，返回现有的；否则创建新的。

        Args:
            uid: 目标用户 ID (required)

        Returns:
            Dictionary containing:
                - roomId: 聊天室 ID

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If user doesn't exist

        API Endpoint:
            GET /api/v3/users/{uid}/chat
        """
        return self._client.get(f"/api/v3/users/{uid}/chat")

    def send_message(
        self,
        room_id: int,
        message: str,
        to_mid: str = "",
    ) -> Dict[str, Any]:
        """Send a message to a chat room.

        Posts a new message to an existing chat room.

        Args:
            room_id: Chat room ID (required)
            message: Message content (required)
            to_mid: Message ID being replied to (optional)

        Returns:
            Dictionary containing:
                - mid: Created message ID
                - content: Message content (HTML)
                - fromuid: Sender user ID
                - timestamp: Message timestamp
                - roomId: Room ID

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user is not in the room
            ValidationError: If message is empty
            ResourceNotFoundError: If room doesn't exist

        API Endpoint:
            POST /api/v3/chats/{room_id}
        """
        # 获取 CSRF token
        from nodebb.api.auth import AuthAPI
        auth = AuthAPI(self._client, self._config)
        csrf_token = auth.get_csrf_token()

        # 使用底层 httpx 客户端直接发送（需要 CSRF token）
        url = f"{self._config.base_url}/api/v3/chats/{room_id}"
        headers = {
            "Content-Type": "application/json",
            "x-csrf-token": csrf_token,
        }
        data = {"message": message, "toMid": to_mid}

        response = self._client.client.post(url, json=data, headers=headers)

        # 处理响应
        if response.status_code >= 400:
            from nodebb.exceptions import APIError
            raise APIError(f"Failed to send message: {response.status_code}")

        result = response.json()
        # 返回 response 字段的内容
        if isinstance(result, dict) and "response" in result:
            return result["response"]
        return result

    def get_messages(
        self,
        room_id: int,
        start: Optional[int] = None,
        count: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get messages from a chat room.

        Retrieves chat history from a room.

        Args:
            room_id: Chat room ID (required)
            start: Start index for pagination (default: 0)
            count: Number of messages to retrieve (default: forum setting)

        Returns:
            Dictionary containing:
                - messages: Array of message objects
                - Each message has: mid, content, fromUid, timestamp, etc.
                - users: User info for message authors
                - nextStart: Index for next page

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user is not in the room
            ResourceNotFoundError: If room doesn't exist

        API Endpoint:
            GET /api/v3/chats/{room_id}/messages
        """
        params = {}
        if start is not None:
            params["start"] = start
        if count is not None:
            params["count"] = count

        return self._client.get(f"/api/v3/chats/{room_id}/messages", params=params)

    def get_room_detail(self, room_id: int) -> Dict[str, Any]:
        """Get detailed information about a chat room.

        Retrieves full room information including all members.

        Args:
            room_id: Chat room ID (required)

        Returns:
            Dictionary containing:
                - roomId: Room ID
                - users: Array of all users in room
                - owner: Room owner user ID
                - isOwner: Whether current user is owner
                - timestamp: Room creation time
                - active: Array of online users
                - etc.

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user is not in the room
            ResourceNotFoundError: If room doesn't exist

        API Endpoint:
            GET /api/v3/chats/{room_id}
        """
        return self._client.get(f"/api/v3/chats/{room_id}")

    def add_users(self, room_id: int, uids: List[int]) -> Dict[str, Any]:
        """Add users to a chat room.

        Invites new users to an existing chat room.

        Args:
            room_id: Chat room ID (required)
            uids: List of user IDs to add (required)

        Returns:
            Dictionary containing:
                - users: Updated list of users in room
                - added: List of successfully added users

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user is not room owner
            ResourceNotFoundError: If room doesn't exist

        API Endpoint:
            PUT /api/v3/chats/{room_id}/users
        """
        return self._client.put(
            f"/api/v3/chats/{room_id}/users",
            data={"uids": uids},
        )

    def leave_room(self, room_id: int, uids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Leave a chat room or remove users from it.

        Removes users from a chat room. If uids is not provided,
        removes the authenticated user from the room (leave operation).

        Args:
            room_id: Chat room ID (required)
            uids: List of user IDs to remove (optional).
                   If None, removes the authenticated user (leave).
                   If provided, removes the specified users.

        Returns:
            Dictionary containing updated room user list

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If room doesn't exist

        API Endpoint:
            DELETE /api/v3/chats/{room_id}/users
        """
        data = {}
        if uids is not None:
            data["uids"] = uids

        return self._client.delete(f"/api/v3/chats/{room_id}/users", data=data)

    def rename_room(self, room_id: int, name: str) -> Dict[str, Any]:
        """Rename a chat room.

        Changes the name of an existing chat room.

        Args:
            room_id: Chat room ID to rename (required)
            name: New room name (required)

        Returns:
            Dictionary containing:
                - roomId: Room ID
                - name: New room name

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user is not room owner
            ResourceNotFoundError: If room doesn't exist

        API Endpoint:
            PUT /api/v3/chats/{room_id}
        """
        return self._client.put(
            f"/api/v3/chats/{room_id}",
            data={"name": name},
        )
