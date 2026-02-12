"""
Read API module for NodeBB.

Handles all GET endpoints that retrieve data from the forum.
These endpoints generally don't require authentication (except user-specific data).
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List


class ReadAPI:
    """Handles read-only API endpoints.

    This class provides methods for retrieving data from NodeBB:
    - Notifications and unread counts
    - Topics and posts
    - Categories
    - User information
    - Forum configuration

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig(base_url="https://forum.example.com")
        >>> client = NodeBBClient(config)
        >>> notifications = client.read.get_notifications()
    """

    def __init__(self, http_client, config):
        """Initialize Read API.

        Args:
            http_client: HTTP client for making requests
            config: NodeBBConfig instance
        """
        self._client = http_client
        self._config = config

    def get_notifications(
        self,
        filter: str = "",
        page: int = 1,
    ) -> Dict[str, Any]:
        """Get user notifications.

        Retrieves notifications for the authenticated user. Supports filtering
        by notification type such as mentions, replies, and chat messages.

        Args:
            filter: Notification type filter. Valid values:
                - '' (empty): All notifications
                - 'new-topic': New topic in watched category
                - 'new-reply': Reply to watched topic
                - 'mention': @mention in a post
                - 'new-chat': New chat message
                - 'new-group-chat': New group chat message
                - 'new-public-chat': New public chat message
                - 'follow': User followed you
                - 'upvote': Your post was upvoted
                - 'new-reward': New reward/badge
                - 'new-post-flag': New flagged post (moderator)
                - 'my-flags': My flagged content (moderator)
                - 'ban': Ban notifications
                - 'new-topic-with-tag': New topic with specific tag
                - 'new-topic-in-category': New topic in specific category
            page: Page number for pagination (default: 1)

        Returns:
            Dictionary containing:
                - notifications: List of notification objects, each with:
                    - nid: Notification ID
                    - type: Notification type (new-reply, new-chat, etc.)
                    - bodyShort: Short HTML description
                    - bodyLong: Full notification content
                    - datetime: UNIX timestamp (ms)
                    - datetimeISO: ISO timestamp
                    - from: Source user ID
                    - user: Source user info (username, picture, etc.)
                    - path: URL path to related content
                    - read: Whether notification has been read
                    - importance: Priority level
                    - mergeId: ID for merging similar notifications
                    - subject: Topic/subject title (if applicable)
                    - tid: Topic ID (for topic-related notifications)
                    - pid: Post ID (for post-related notifications)
                    - roomId: Chat room ID (for chat notifications)
                - filters: Available filter types with counts
                - regularFilters: Regular notification filters
                - moderatorFilters: Moderator-only filters
                - selectedFilter: Currently selected filter
                - pagination: Pagination info

        Raises:
            AuthenticationError: If authentication required but not provided
            NetworkError: If network request fails

        API Endpoint:
            GET /api/notifications
        """
        params = {}
        if filter:
            params["filter"] = filter

        return self._client.get("/api/notifications", params=params)

    def get_unread_count(self) -> int:
        """Get total count of unread topics.

        Returns the number of topics the authenticated user hasn't read yet.

        Returns:
            Number of unread topics

        Raises:
            AuthenticationError: If authentication required but not provided
            NetworkError: If network request fails

        API Endpoint:
            GET /api/unread/total
        """
        result = self._client.get("/api/unread/total")
        # API returns raw number as text/plain
        if isinstance(result, (int, str)):
            return int(result)
        return 0

    def get_unread_topics(
        self,
        start: Optional[int] = None,
        per_page: Optional[int] = None,
        filter: str = "",
    ) -> Dict[str, Any]:
        """Get list of unread topics.

        Retrieves topics that the authenticated user hasn't read yet,
        sorted by the most recent post timestamp.

        Args:
            start: Start index for pagination (default: 0)
            per_page: Number of topics per page (default: forum setting)
            filter: Topic filter type. Valid values:
                - '' (empty): All unread topics (default)
                - 'new': New topics only
                - 'watched': Watched topics only
                - 'unreplied': Topics with no replies

        Returns:
            Dictionary containing:
                - topics: List of unread topic objects, each with:
                    - tid: Topic ID
                    - title: Topic title
                    - slug: URL slug
                    - cid: Category ID
                    - uid: Author user ID
                    - postcount: Number of posts
                    - viewcount: Number of views
                    - timestamp: Creation timestamp (UNIX ms)
                    - timestampISO: ISO timestamp
                    - lastposttime: Last post timestamp
                    - user: Author info (username, picture, etc.)
                    - category: Category info (name, icon, color, etc.)
                    - teaser: Latest post preview (pid, content, user)
                    - tags: List of tags
                    - unread: Whether topic is unread
                    - followed: Whether user follows this topic
                - nextStart: Index for next page
                - topicCount: Total number of unread topics
                - filters: Available filter options
                - selectedFilter: Currently selected filter

        Raises:
            AuthenticationError: If authentication required but not provided
            NetworkError: If network request fails

        API Endpoint:
            GET /api/unread
        """
        params = {}
        if start is not None:
            params["start"] = start
        if per_page is not None:
            params["per_page"] = per_page
        if filter:
            params["filter"] = filter

        return self._client.get("/api/unread", params=params)

    def get_recent_posts(
        self,
        term: str = "all",
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get recent posts from the forum.

        Retrieves posts filtered by time period. Useful for showing recent activity.

        Args:
            term: Time period filter. Valid values:
                - 'all': All posts (no time limit)
                - 'day': Posts from last 24 hours
                - 'week': Posts from last 7 days
                - 'month': Posts from last 30 days
            page: Page number for pagination

        Returns:
            Dictionary containing:
                - posts: List of post objects
                - nextStart: Index for next page (if applicable)
                - pagination info

        Raises:
            NetworkError: If network request fails

        API Endpoint:
            GET /api/recent/posts/{term}
        """
        params = {}
        if page is not None:
            params["page"] = page

        return self._client.get(f"/api/recent/posts/{term}", params=params)

    def get_topic(
        self,
        tid: int,
        slug: str = "",
        post_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get a topic and its posts.

        Retrieves full topic data including all posts in the thread.

        Args:
            tid: Topic ID (required)
            slug: Topic URL slug (optional, auto-redirects if omitted)
            post_index: Post index to jump to (optional)

        Returns:
            Dictionary containing:
                - topic data (title, posts, category, etc.)
                - posts: Array of post objects
                - pagination info
                - privileges: User's permissions for this topic
                - isFollowing: Whether user follows this topic

        Raises:
            ResourceNotFoundError: If topic doesn't exist
            NetworkError: If network request fails

        API Endpoint:
            GET /api/topic/{tid}/{slug}/{post_index}
        """
        slug = slug or "_"
        path = f"/api/topic/{tid}/{slug}"
        if post_index is not None:
            path += f"/{post_index}"

        return self._client.get(path)

    def get_categories(self) -> Dict[str, Any]:
        """Get all categories from the forum.

        Retrieves the full category tree including subcategories.

        Returns:
            Dictionary containing:
                - categories: List of category objects
                - Each category has: cid, name, description, icon, etc.

        Raises:
            NetworkError: If network request fails

        API Endpoint:
            GET /api/categories
        """
        return self._client.get("/api/categories")

    def get_category(
        self,
        cid: int,
        slug: str = "",
        topic_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get a single category with its topics.

        Retrieves category details and topics within it.

        Args:
            cid: Category ID (required)
            slug: Category URL slug (optional, auto-redirects if omitted)
            topic_index: Topic index for pagination (optional)

        Returns:
            Dictionary containing:
                - category data (name, description, etc.)
                - children: Array of child categories
                - topics: List of topics in this category
                - pagination info (nextStart, etc.)
                - privileges: User's permissions for this category

        Raises:
            ResourceNotFoundError: If category doesn't exist
            NetworkError: If network request fails

        API Endpoint:
            GET /api/category/{cid}/{slug}/{topic_index}
        """
        slug = slug or "_"
        path = f"/api/category/{cid}/{slug}"
        if topic_index is not None:
            path += f"/{topic_index}"

        return self._client.get(path)

    def get_user(self, uid: int) -> Dict[str, Any]:
        """Get user information by user ID.

        Retrieves public profile data for a user.

        Args:
            uid: User ID (required)

        Returns:
            Dictionary containing user data:
                - uid: User ID
                - username: Username
                - userslug: URL-safe username
                - picture: Avatar URL
                - postcount: Number of posts
                - reputation: Reputation score
                - joindate: Account creation timestamp
                - status: Custom status message
                - groups: User group memberships
                - etc.

        Raises:
            ResourceNotFoundError: If user doesn't exist
            NetworkError: If network request fails

        API Endpoint:
            GET /api/user/uid/{uid}
        """
        return self._client.get(f"/api/user/uid/{uid}")

    def get_user_by_username(self, userslug: str) -> Dict[str, Any]:
        """Get user information by username slug.

        Same as get_user but uses username slug instead of UID.

        Args:
            userslug: URL-safe username (required)

        Returns:
            Dictionary containing user data (same format as get_user)

        Raises:
            ResourceNotFoundError: If user doesn't exist
            NetworkError: If network request fails

        API Endpoint:
            GET /api/user/{userslug}
        """
        return self._client.get(f"/api/user/{userslug}")

    def search_users(
        self,
        query: str = "",
        section: str = "joindate",
        page: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Search for users.

        Searches for users matching a query string.

        Args:
            query: Search term (empty returns all users)
            section: Sort/filter section. Valid values:
                - 'joindate': Sort by join date (default)
                - 'online': Only online users
                - 'sort-posts': Sort by post count
                - 'sort-reputation': Sort by reputation
                - 'banned': Banned users
                - 'flagged': Flagged users
            page: Page number for pagination

        Returns:
            Dictionary containing:
                - users: Array of user objects
                - userCount: Total matching users
                - pagination info

        Raises:
            NetworkError: If network request fails

        API Endpoint:
            GET /api/users
        """
        params = {"section": section}
        if query:
            params["term"] = query
        if page is not None:
            params["page"] = page

        return self._client.get("/api/users", params=params)

    def get_config(self) -> Dict[str, Any]:
        """Get forum configuration.

        Retrieves global forum settings and configuration.

        Returns:
            Dictionary containing forum config:
                - minimumTitleLength: Min topic title length
                - maximumTitleLength: Max topic title length
                - minimumPostLength: Min post content length
                - maximumPostLength: Max post content length
                - postDelay: Minimum seconds between posts
                - reputation:disbaled: If reputation system is disabled
                - downvote:disabled: If downvotes are disabled
                - etc.

        Raises:
            NetworkError: If network request fails

        API Endpoint:
            GET /api/config
        """
        return self._client.get("/api/config")

    def get_post(self, pid: int) -> Dict[str, Any]:
        """Get a single post by ID.

        Retrieves full post data including content and metadata.

        Args:
            pid: Post ID (required)

        Returns:
            Dictionary containing:
                - pid: Post ID
                - content: Post content (may be parsed or raw)
                - user: Author information
                - tid: Topic ID
                - timestamp: Post timestamp
                - upvotes/downvotes: Vote counts
                - edited: Edit timestamp (if edited)
                - etc.

        Raises:
            ResourceNotFoundError: If post doesn't exist
            NetworkError: If network request fails

        API Endpoint:
            GET /api/post/{pid}
        """
        return self._client.get(f"/api/post/{pid}")
