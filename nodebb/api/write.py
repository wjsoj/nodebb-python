"""
Write API module for NodeBB.

Handles all POST/PUT/DELETE endpoints that modify forum data.
All endpoints in this module require authentication.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List


class WriteAPI:
    """Handles write/modification API endpoints.

    This class provides methods for creating and modifying content:
    - Creating topics and replies
    - Editing and deleting posts
    - Voting and bookmarking
    - Following topics
    - Topic state management (lock/unlock, pin/unpin)
    - Topic tag management
    - Post operations (move, state/restore)
    - Category operations

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig.for_user_token("https://forum.example.com", "token")
        >>> client = NodeBBClient(config)
        >>> topic = client.write.create_topic(cid=1, title="Test", content="Hello")
    """

    def __init__(self, http_client, config):
        """Initialize Write API.

        Args:
            http_client: HTTP client for making requests
            config: NodeBBConfig instance
        """
        self._client = http_client
        self._config = config

    # ====================================================================
    # Topic Operations
    # ====================================================================

    def create_topic(
        self,
        cid: int,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        timestamp: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a new topic.

        Creates a new topic in the specified category.

        Args:
            cid: Category ID to post in (required)
            title: Topic title (required, must be >3 characters)
            content: Post content in Markdown (required, must be >8 characters)
            tags: Optional list of tag strings
            timestamp: Optional UNIX timestamp for scheduled posting
                    (requires topics:schedule privilege)

        Returns:
            Dictionary containing:
                - tid: Created topic ID
                - pid: Main post ID
                - topic data (title, slug, timestamp, etc.)

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'topics:create' privilege
            ValidationError: If title/content is invalid or too short

        API Endpoint:
            POST /api/v3/topics/
        """
        # 获取 CSRF token
        from nodebb.api.auth import AuthAPI
        auth = AuthAPI(self._client, self._config)
        csrf_token = auth.get_csrf_token()

        data = {
            "cid": cid,
            "title": title,
            "content": content,
        }
        if tags:
            data["tags"] = tags
        if timestamp is not None:
            data["timestamp"] = timestamp

        # 使用底层 httpx 客户端并添加 CSRF token
        url = f"{self._config.base_url}/api/v3/topics/"
        headers = {
            "Content-Type": "application/json",
            "x-csrf-token": csrf_token,
        }

        response = self._client.client.post(url, json=data, headers=headers)

        if response.status_code >= 400:
            from nodebb.exceptions import APIError
            raise APIError(f"Failed to create topic: {response.status_code} - {response.text[:100]}")

        result = response.json()
        # 返回 response 字段的内容
        if isinstance(result, dict) and "response" in result:
            return result["response"]
        return result

    def create_reply(
        self,
        tid: int,
        content: str,
        to_pid: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Reply to an existing topic.

        Creates a new post replying to a topic or specific post.

        Args:
            tid: Topic ID to reply to (required)
            content: Reply content in Markdown (required, must be >8 characters)
            to_pid: Optional post ID being replied to (for nested replies)

        Returns:
            Dictionary containing:
                - pid: Created post ID
                - tid: Topic ID
                - content: Post content
                - timestamp: Creation timestamp
                - user: Author info
                - index: Post position in topic

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'topics:reply' privilege
            ValidationError: If content is too short
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            POST /api/v3/topics/{tid}
        """
        # 获取 CSRF token
        from nodebb.api.auth import AuthAPI
        auth = AuthAPI(self._client, self._config)
        csrf_token = auth.get_csrf_token()

        data = {"content": content}
        if to_pid is not None:
            data["toPid"] = to_pid

        # 使用底层 httpx 客户端并添加 CSRF token
        url = f"{self._config.base_url}/api/v3/topics/{tid}"
        headers = {
            "Content-Type": "application/json",
            "x-csrf-token": csrf_token,
        }

        response = self._client.client.post(url, json=data, headers=headers)

        if response.status_code >= 400:
            from nodebb.exceptions import APIError
            raise APIError(f"Failed to reply: {response.status_code} - {response.text[:100]}")

        result = response.json()
        # 返回 response 字段的内容
        if isinstance(result, dict) and "response" in result:
            return result["response"]
        return result

    def delete_topic(self, tid: int) -> Dict[str, Any]:
        """Delete/purge a topic and all its posts.

        Permanently removes a topic and all posts within it.

        Args:
            tid: Topic ID to delete (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'topics:delete' or purge privilege
            ResourceNotFoundError: If topic doesn't exist

        Warning:
            This action cannot be undone. Use with caution.

        API Endpoint:
            DELETE /api/v3/topics/{tid}
        """
        return self._client.delete(f"/api/v3/topics/{tid}")

    # ====================================================================
    # Topic State Operations
    # ====================================================================

    def set_topic_state(self, tid: int, state: str) -> Dict[str, Any]:
        """Set the state of a topic (locked/unlocked).

        Locked topics cannot be replied to (except by admins).

        Args:
            tid: Topic ID (required)
            state: State to set: 'locked' or 'unlocked'

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks moderation privileges
            ValidationError: If state is not valid
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            PUT /api/v3/topics/{tid}/state
        """
        params = {"state": state}
        return self._client.put(f"/api/v3/topics/{tid}/state", data=params)

    def pin_topic(self, tid: int, expiry: Optional[int] = None) -> Dict[str, Any]:
        """Pin a topic to the top of the topic list.

        Pinned topics are shown at the top of topic lists.

        Args:
            tid: Topic ID to pin (required)
            expiry: Optional UNIX timestamp for auto-unpin (default: indefinite)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks moderation privileges
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            PUT /api/v3/topics/{tid}/pin
        """
        data = {}
        if expiry is not None:
            data["expiry"] = expiry
        return self._client.put(f"/api/v3/topics/{tid}/pin", data=data)

    def unpin_topic(self, tid: int) -> Dict[str, Any]:
        """Unpin a topic from the top of the topic list.

        Removes the pin status from a topic.

        Args:
            tid: Topic ID to unpin (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            DELETE /api/v3/topics/{tid}/pin
        """
        return self._client.delete(f"/api/v3/topics/{tid}/pin")

    # ====================================================================
    # Topic Tag Operations
    # ====================================================================

    def update_topic_tags(self, tid: int, tags: List[str]) -> Dict[str, Any]:
        """Update all tags on a topic (replaces existing tags).

        Updates all tags on a topic with the provided list.

        Args:
            tid: Topic ID (required)
            tags: Complete list of tags (replaces all existing)

        Returns:
            Updated array of topic tags

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'topics:tag' privilege
            ValidationError: If tags list is empty
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            PUT /api/v3/topics/{tid}/tags
        """
        return self._client.put(f"/api/v3/topics/{tid}/tags", data={"tags": tags})

    def add_topic_tag(self, tid: int, tag: str) -> Dict[str, Any]:
        """Add a single tag to a topic.

        Adds a new tag to the topic's existing tags.

        Args:
            tid: Topic ID (required)
            tag: Tag string to add

        Returns:
            Updated array of topic tags

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'topics:tag' privilege
            ValidationError: If tag is empty
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            PATCH /api/v3/topics/{tid}/tags
        """
        if not tag:
            raise ValueError("Tag cannot be empty")
        return self._client.patch(f"/api/v3/topics/{tid}/tags", data={"tags": [tag]})

    def remove_topic_tags(self, tid: int) -> Dict[str, Any]:
        """Remove all tags from a topic.

        Removes all tags associated with a topic.

        Args:
            tid: Topic ID (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'topics:tag' privilege
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            DELETE /api/v3/topics/{tid}/tags
        """
        return self._client.delete(f"/api/v3/topics/{tid}/tags")

    # ====================================================================
    # Post Operations
    # ====================================================================

    def edit_post(
        self,
        pid: int,
        content: str,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Edit a post.

        Modifies an existing post's content.

        Args:
            pid: Post ID to edit (required)
            content: New content in Markdown (required)
            title: New title (only for main posts, optional)

        Returns:
            Dictionary containing:
                - pid: Post ID
                - content: Updated content
                - edited: Edit timestamp
                - etc.

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'posts:edit' privilege
            ValidationError: If content is invalid
            ResourceNotFoundError: If post doesn't exist

        API Endpoint:
            PUT /api/v3/posts/{pid}
        """
        data = {"content": content}
        if title is not None:
            data["title"] = title

        return self._client.put(f"/api/v3/posts/{pid}", data=data)

    def delete_post(self, pid: int) -> Dict[str, Any]:
        """Delete/purge a post.

        Permanently removes a post from the forum.

        Args:
            pid: Post ID to delete (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks 'posts:delete' or purge privilege
            ResourceNotFoundError: If post doesn't exist

        API Endpoint:
            DELETE /api/v3/posts/{pid}
        """
        return self._client.delete(f"/api/v3/posts/{pid}")

    def move_post(self, pid: int, tid: int) -> Dict[str, Any]:
        """Move a post to a different topic.

        Moves a post from its current topic to a target topic.

        Args:
            pid: Post ID to move (required)
            tid: Target topic ID (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks post move privileges
            ValidationError: If parameters are invalid
            ResourceNotFoundError: If post or topic doesn't exist

        API Endpoint:
            PUT /api/v3/posts/{pid}/move
        """
        return self._client.put(f"/api/v3/posts/{pid}/move", data={"tid": tid})

    # ====================================================================
    # Post State Operations
    # ====================================================================

    def restore_post(self, pid: int) -> Dict[str, Any]:
        """Restore a soft-deleted post.

        Restores a post that has been soft deleted back to its original state.

        Args:
            pid: Post ID to restore (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks post restore privileges
            ResourceNotFoundError: If post doesn't exist

        API Endpoint:
            PUT /api/v3/posts/{pid}/state
        """
        return self._client.put(f"/api/v3/posts/{pid}/state", data={})

    def soft_delete_post(self, pid: int) -> Dict[str, Any]:
        """Soft delete a post.

        Soft deletes a post, making it invisible to regular users
        but restorable by moderators.

        Args:
            pid: Post ID to soft delete (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks delete privileges

        Note:
            Soft deleted posts can be restored with restore_post().

        API Endpoint:
            DELETE /api/v3/posts/{pid}/state
        """
        return self._client.delete(f"/api/v3/posts/{pid}/state")

    def get_post_replies(
        self,
        pid: int,
        start: Optional[int] = None,
        direction: str = "-1",
        per_page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get direct replies to a post.

        Retrieves all direct replies to a specific post.

        Args:
            pid: Post ID to get replies for (required)
            start: Start index for pagination (optional)
            direction: Sort direction. '-1' for newest first,
                     '1' for oldest first (default: '-1')
            per_page: Number of replies per page (optional)

        Returns:
            Dictionary containing:
                - replies: Array of reply objects
                - Each reply has: pid, uid, tid, content, timestamp,
                  votes, upvotes, downvotes, user data, etc.
                - pagination info

        Raises:
            ResourceNotFoundError: If post doesn't exist
            NetworkError: If network request fails

        API Endpoint:
            GET /api/v3/posts/{pid}/replies
        """
        params = {}
        if start is not None:
            params["start"] = start
        if direction:
            params["direction"] = direction
        if per_page is not None:
            params["per_page"] = per_page

        return self._client.get(f"/api/v3/posts/{pid}/replies", params=params)

    # ====================================================================
    # Post Voting and Bookmarking
    # ====================================================================

    def vote_post(self, pid: int, delta: int = 1) -> Dict[str, Any]:
        """Vote on a post (upvote or downvote).

        Casts a vote on a post.

        Args:
            pid: Post ID to vote on (required)
            delta: Vote value (default: 1 for upvote)
                    - Positive: Upvote
                    - Negative: Downvote
                    - 0: Remove vote (use unvote_post instead)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            PrivilegeError: If user lacks voting privileges
            ResourceNotFoundError: If post doesn't exist

        Note:
            Use delta=0 or unvote_post() to remove a vote.

        API Endpoint:
            PUT /api/v3/posts/{pid}/vote
        """
        return self._client.put(f"/api/v3/posts/{pid}/vote", data={"delta": delta})

    def unvote_post(self, pid: int) -> Dict[str, Any]:
        """Remove vote from a post.

        Clears any existing vote on a post.

        Args:
            pid: Post ID to unvote (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If post doesn't exist

        API Endpoint:
            DELETE /api/v3/posts/{pid}/vote
        """
        return self._client.delete(f"/api/v3/posts/{pid}/vote")

    def bookmark_post(self, pid: int) -> Dict[str, Any]:
        """Bookmark a post.

        Adds post to user's bookmarks.

        Args:
            pid: Post ID to bookmark (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If post doesn't exist

        API Endpoint:
            PUT /api/v3/posts/{pid}/bookmark
        """
        return self._client.put(f"/api/v3/posts/{pid}/bookmark", data={})

    def unbookmark_post(self, pid: int) -> Dict[str, Any]:
        """Remove bookmark from a post.

        Removes post from user's bookmarks.

        Args:
            pid: Post ID to unbookmark (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If post doesn't exist

        API Endpoint:
            DELETE /api/v3/posts/{pid}/bookmark
        """
        return self._client.delete(f"/api/v3/posts/{pid}/bookmark")

    # ====================================================================
    # Topic Following
    # ====================================================================

    def follow_topic(self, tid: int) -> Dict[str, Any]:
        """Follow/watch a topic.

        Subscribe to notifications for new posts in this topic.

        Args:
            tid: Topic ID to follow (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            PUT /api/v3/topics/{tid}/follow
        """
        return self._client.put(f"/api/v3/topics/{tid}/follow", data={})

    def unfollow_topic(self, tid: int) -> Dict[str, Any]:
        """Unfollow/unwatch a topic.

        Unsubscribe from notifications for this topic.

        Args:
            tid: Topic ID to unfollow (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            DELETE /api/v3/topics/{tid}/follow
        """
        return self._client.delete(f"/api/v3/topics/{tid}/follow")

    def mark_topic_read(self, tid: int) -> Dict[str, Any]:
        """Mark a topic as read.

        Clears the unread status for this topic.

        Args:
            tid: Topic ID to mark read (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            PUT /api/v3/topics/{tid}/read
        """
        return self._client.put(f"/api/v3/topics/{tid}/read", data={})

    def mark_topic_unread(self, tid: int) -> Dict[str, Any]:
        """Mark a topic as unread.

        Sets the unread status for this topic.

        Args:
            tid: Topic ID to mark unread (required)

        Returns:
            Empty dictionary on success

        Raises:
            AuthenticationError: If not authenticated
            ResourceNotFoundError: If topic doesn't exist

        API Endpoint:
            DELETE /api/v3/topics/{tid}/read
        """
        return self._client.delete(f"/api/v3/topics/{tid}/read")
