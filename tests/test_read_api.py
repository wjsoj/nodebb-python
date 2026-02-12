"""Tests for Read API endpoints.

These tests verify the structure and interface of ReadAPI methods.
Note: These are unit tests and don't make actual API calls.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from nodebb.api.read import ReadAPI
from nodebb.config import NodeBBConfig
from nodebb.exceptions import AuthenticationError, ResourceNotFoundError


class TestReadAPI:
    """Test cases for Read API module."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return NodeBBConfig(
            base_url="https://test.example.com",
            user_token="test_token"
        )

    @pytest.fixture
    def mock_client(self, config):
        """Create API with mocked HTTP client."""
        mock_http = MagicMock()
        return ReadAPI(mock_http, config)

    # ====================================================================
    # Tests: get_notifications
    # ====================================================================

    def test_get_notifications_default_params(self, mock_client):
        """Test get_notifications with default parameters."""
        mock_client._client.get.return_value = {"notifications": []}

        result = mock_client.get_notifications()

        mock_client._client.get.assert_called_once_with("/api/notifications", params={})
        assert result == {"notifications": []}

    def test_get_notifications_with_filter(self, mock_client):
        """Test get_notifications with filter parameter."""
        mock_client._client.get.return_value = {"notifications": []}

        result = mock_client.get_notifications(filter="new-mention")

        mock_client._client.get.assert_called_once_with(
            "/api/notifications", params={"filter": "new-mention"}
        )
        assert result == {"notifications": []}

    def test_get_notifications_with_page(self, mock_client):
        """Test get_notifications with page parameter."""
        mock_client._client.get.return_value = {"notifications": []}

        result = mock_client.get_notifications(page=2)

        mock_client._client.get.assert_called_once_with("/api/notifications", params={"page": 2})
        assert result == {"notifications": []}

    # ====================================================================
    # Tests: get_unread_count
    # ====================================================================

    def test_get_unread_count(self, mock_client):
        """Test get_unread_count returns integer."""
        mock_client._client.get.return_value = 5

        result = mock_client.get_unread_count()

        mock_client._client.get.assert_called_once_with("/api/unread/total")
        assert result == 5

    def test_get_unread_count_zero(self, mock_client):
        """Test get_unread_count handles zero response."""
        mock_client._client.get.return_value = 0

        result = mock_client.get_unread_count()

        assert result == 0

    # ====================================================================
    # Tests: get_unread_topics
    # ====================================================================

    def test_get_unread_topics_default(self, mock_client):
        """Test get_unread_topics with defaults."""
        mock_client._client.get.return_value = {"topics": []}

        result = mock_client.get_unread_topics()

        mock_client._client.get.assert_called_once_with("/api/unread", params={})
        assert result == {"topics": []}

    def test_get_unread_topics_with_pagination(self, mock_client):
        """Test get_unread_topics with pagination."""
        mock_client._client.get.return_value = {"topics": []}

        result = mock_client.get_unread_topics(start=10, per_page=20)

        mock_client._client.get.assert_called_once_with(
            "/api/unread", params={"start": 10, "per_page": 20}
        )
        assert result == {"topics": []}

    # ====================================================================
    # Tests: get_recent_posts
    # ====================================================================

    def test_get_recent_posts_default_term(self, mock_client):
        """Test get_recent_posts with default term."""
        mock_client._client.get.return_value = {"posts": []}

        result = mock_client.get_recent_posts()

        mock_client._client.get.assert_called_once_with("/api/recent/posts/all", params={})
        assert result == {"posts": []}

    def test_get_recent_posts_day_term(self, mock_client):
        """Test get_recent_posts with day term."""
        mock_client._client.get.return_value = {"posts": []}

        result = mock_client.get_recent_posts(term="day")

        mock_client._client.get.assert_called_once_with("/api/recent/posts/day", params={})
        assert result == {"posts": []}

    def test_get_recent_posts_with_page(self, mock_client):
        """Test get_recent_posts with page parameter."""
        mock_client._client.get.return_value = {"posts": []}

        result = mock_client.get_recent_posts(term="week", page=2)

        mock_client._client.get.assert_called_once_with(
            "/api/recent/posts/week", params={"page": 2}
        )
        assert result == {"posts": []}

    # ====================================================================
    # Tests: get_topic
    # ====================================================================

    def test_get_topic_minimal(self, mock_client):
        """Test get_topic with only required tid."""
        mock_client._client.get.return_value = {"tid": 1}

        result = mock_client.get_topic(tid=123)

        mock_client._client.get.assert_called_once_with("/api/topic/123/_")
        assert result == {"tid": 1}

    def test_get_topic_with_slug(self, mock_client):
        """Test get_topic with slug."""
        mock_client._client.get.return_value = {"tid": 1}

        result = mock_client.get_topic(tid=123, slug="my-topic")

        mock_client._client.get.assert_called_once_with("/api/topic/123/my-topic")
        assert result == {"tid": 1}

    def test_get_topic_with_post_index(self, mock_client):
        """Test get_topic with post_index."""
        mock_client._client.get.return_value = {"tid": 1}

        result = mock_client.get_topic(tid=123, post_index=5)

        mock_client._client.get.assert_called_once_with("/api/topic/123/_/5")
        assert result == {"tid": 1}

    # ====================================================================
    # Tests: get_categories
    # ====================================================================

    def test_get_categories(self, mock_client):
        """Test get_categories."""
        mock_client._client.get.return_value = {"categories": []}

        result = mock_client.get_categories()

        mock_client._client.get.assert_called_once_with("/api/categories", params=None)
        assert result == {"categories": []}

    # ====================================================================
    # Tests: get_category
    # ====================================================================

    def test_get_category_minimal(self, mock_client):
        """Test get_category with only cid."""
        mock_client._client.get.return_value = {"cid": 1}

        result = mock_client.get_category(cid=5)

        mock_client._client.get.assert_called_once_with("/api/category/5/_")
        assert result == {"cid": 1}

    def test_get_category_with_slug(self, mock_client):
        """Test get_category with slug."""
        mock_client._client.get.return_value = {"cid": 1}

        result = mock_client.get_category(cid=5, slug="general")

        mock_client._client.get.assert_called_once_with("/api/category/5/general")
        assert result == {"cid": 1}

    # ====================================================================
    # Tests: get_user
    # ====================================================================

    def test_get_user(self, mock_client):
        """Test get_user by uid."""
        mock_client._client.get.return_value = {"uid": 123, "username": "test"}

        result = mock_client.get_user(uid=123)

        mock_client._client.get.assert_called_once_with("/api/user/uid/123")
        assert result["username"] == "test"

    def test_get_user_by_username(self, mock_client):
        """Test get_user_by_username."""
        mock_client._client.get.return_value = {"uid": 123, "username": "test"}

        result = mock_client.get_user_by_username(userslug="test")

        mock_client._client.get.assert_called_once_with("/api/user/test")
        assert result["username"] == "test"

    # ====================================================================
    # Tests: search_users
    # ====================================================================

    def test_search_users_default(self, mock_client):
        """Test search_users with default section."""
        mock_client._client.get.return_value = {"users": []}

        result = mock_client.search_users()

        mock_client._client.get.assert_called_once_with(
            "/api/users", params={"section": "joindate"}
        )
        assert result == {"users": []}

    def test_search_users_with_query(self, mock_client):
        """Test search_users with query."""
        mock_client._client.get.return_value = {"users": []}

        result = mock_client.search_users(query="john")

        mock_client._client.get.assert_called_once_with(
            "/api/users", params={"section": "joindate", "term": "john"}
        )
        assert result == {"users": []}

    def test_search_users_online_section(self, mock_client):
        """Test search_users with online section."""
        mock_client._client.get.return_value = {"users": []}

        result = mock_client.search_users(query="", section="online")

        mock_client._client.get.assert_called_once_with(
            "/api/users", params={"section": "online", "term": ""}
        )
        assert result == {"users": []}

    # ====================================================================
    # Tests: get_config
    # ====================================================================

    def test_get_config(self, mock_client):
        """Test get_config."""
        mock_client._client.get.return_value = {"postDelay": 10}

        result = mock_client.get_config()

        mock_client._client.get.assert_called_once_with("/api/config", params=None)
        assert result["postDelay"] == 10

    def test_get_post(self, mock_client):
        """Test get_post."""
        mock_client._client.get.return_value = {"pid": 1, "content": "test"}

        result = mock_client.get_post(pid=1)

        mock_client._client.get.assert_called_once_with("/api/post/1")
        assert result["content"] == "test"


class TestReadAPIDocCoverage:
    """Verify all methods have docstrings and type hints."""

    @pytest.fixture
    def read_api(self):
        """Create ReadAPI instance for testing."""
        config = NodeBBConfig(base_url="https://test.com", user_token="token")
        mock_http = MagicMock()
        return ReadAPI(mock_http, config)

    def test_all_methods_have_docstrings(self, read_api):
        """Verify all public methods have docstrings."""
        methods = [
            read_api.get_notifications,
            read_api.get_unread_count,
            read_api.get_unread_topics,
            read_api.get_recent_posts,
            read_api.get_topic,
            read_api.get_categories,
            read_api.get_category,
            read_api.get_user,
            read_api.get_user_by_username,
            read_api.search_users,
            read_api.get_config,
            read_api.get_post,
        ]

        for method in methods:
            assert method.__doc__ is not None, f"Missing docstring: {method.__name__}"

    def test_method_signatures(self, read_api):
        """Verify method signatures are consistent."""
        # Each method should have proper type hints
        import inspect
        methods = [
            read_api.get_notifications,
            read_api.get_unread_count,
            read_api.get_topic,
        ]

        for method in methods:
            sig = inspect.signature(method)
            # Check return type annotation
            assert sig.return_annotation != inspect.Parameter.empty, f"No return hint: {method.__name__}"
