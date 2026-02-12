"""Tests for Write API endpoints.

These tests verify the structure and interface of WriteAPI methods.
"""

import pytest
from unittest.mock import MagicMock

from nodebb.api.write import WriteAPI
from nodebb.config import NodeBBConfig


class TestWriteAPI:
    """Test cases for Write API module."""

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
        return WriteAPI(mock_http, config)

    # ====================================================================
    # Tests: create_topic
    # ====================================================================

    def test_create_topic_minimal(self, mock_client):
        """Test create_topic with minimal parameters."""
        mock_client._client.post.return_value = {"tid": 1, "pid": 100}

        result = mock_client.create_topic(cid=1, title="Test", content="Hello")

        mock_client._client.post.assert_called_once_with(
            "/api/v3/topics/",
            data={"cid": 1, "title": "Test", "content": "Hello"},
        )
        assert result["tid"] == 1

    def test_create_topic_with_tags(self, mock_client):
        """Test create_topic with tags parameter."""
        mock_client._client.post.return_value = {"tid": 1}

        result = mock_client.create_topic(
            cid=1,
            title="Test",
            content="Hello",
            tags=["test", "example"]
        )

        called_data = mock_client._client.post.call_args[1]["data"]
        assert "tags" in called_data
        assert called_data["tags"] == ["test", "example"]

    def test_create_topic_with_timestamp(self, mock_client):
        """Test create_topic with timestamp parameter."""
        mock_client._client.post.return_value = {"tid": 1}

        result = mock_client.create_topic(
            cid=1,
            title="Test",
            content="Hello",
            timestamp=1234567890
        )

        called_data = mock_client._client.post.call_args[1]["data"]
        assert "timestamp" in called_data
        assert called_data["timestamp"] == 1234567890

    # ====================================================================
    # Tests: create_reply
    # ====================================================================

    def test_create_reply_minimal(self, mock_client):
        """Test create_reply with minimal parameters."""
        mock_client._client.post.return_value = {"pid": 200}

        result = mock_client.create_reply(tid=1, content="Reply")

        mock_client._client.post.assert_called_once_with(
            "/api/v3/topics/1",
            data={"content": "Reply"},
        )
        assert result["pid"] == 200

    def test_create_reply_with_to_pid(self, mock_client):
        """Test create_reply with toPid parameter."""
        mock_client._client.post.return_value = {"pid": 200}

        result = mock_client.create_reply(tid=1, content="Reply", to_pid=100)

        called_data = mock_client._client.post.call_args[1]["data"]
        assert "toPid" in called_data
        assert called_data["toPid"] == 100

    # ====================================================================
    # Tests: delete_topic
    # ====================================================================

    def test_delete_topic(self, mock_client):
        """Test delete_topic."""
        mock_client._client.delete.return_value = {}

        result = mock_client.delete_topic(tid=1)

        mock_client._client.delete.assert_called_once_with("/api/v3/topics/1")
        assert result == {}

    # ====================================================================
    # Tests: edit_post
    # ====================================================================

    def test_edit_post_minimal(self, mock_client):
        """Test edit_post with minimal parameters."""
        mock_client._client.put.return_value = {"pid": 1}

        result = mock_client.edit_post(pid=1, content="New content")

        mock_client._client.put.assert_called_once_with(
            "/api/v3/posts/1",
            data={"content": "New content"},
        )
        assert result["pid"] == 1

    def test_edit_post_with_title(self, mock_client):
        """Test edit_post with title parameter."""
        mock_client._client.put.return_value = {"pid": 1}

        result = mock_client.edit_post(pid=1, content="New content", title="New title")

        called_data = mock_client._client.put.call_args[1]["data"]
        assert "title" in called_data
        assert called_data["title"] == "New title"

    # ====================================================================
    # Tests: delete_post
    # ====================================================================

    def test_delete_post(self, mock_client):
        """Test delete_post."""
        mock_client._client.delete.return_value = {}

        result = mock_client.delete_post(pid=1)

        mock_client._client.delete.assert_called_once_with("/api/v3/posts/1")
        assert result == {}

    # ====================================================================
    # Tests: vote_post
    # ====================================================================

    def test_vote_post_default(self, mock_client):
        """Test vote_post with default delta."""
        mock_client._client.put.return_value = {}

        result = mock_client.vote_post(pid=1)

        called_data = mock_client._client.put.call_args[1]["data"]
        assert called_data == {"delta": 1}

    def test_vote_post_custom_delta(self, mock_client):
        """Test vote_post with custom delta."""
        mock_client._client.put.return_value = {}

        result = mock_client.vote_post(pid=1, delta=-1)

        called_data = mock_client._client.put.call_args[1]["data"]
        assert called_data == {"delta": -1}

    # ====================================================================
    # Tests: unvote_post
    # ====================================================================

    def test_unvote_post(self, mock_client):
        """Test unvote_post."""
        mock_client._client.delete.return_value = {}

        result = mock_client.unvote_post(pid=1)

        mock_client._client.delete.assert_called_once_with("/api/v3/posts/1/vote")
        assert result == {}

    # ====================================================================
    # Tests: bookmark/unbookmark
    # ====================================================================

    def test_bookmark_post(self, mock_client):
        """Test bookmark_post."""
        mock_client._client.put.return_value = {}

        result = mock_client.bookmark_post(pid=1)

        mock_client._client.put.assert_called_once_with("/api/v3/posts/1/bookmark", data={})
        assert result == {}

    def test_unbookmark_post(self, mock_client):
        """Test unbookmark_post."""
        mock_client._client.delete.return_value = {}

        result = mock_client.unbookmark_post(pid=1)

        mock_client._client.delete.assert_called_once_with("/api/v3/posts/1/bookmark")
        assert result == {}

    # ====================================================================
    # Tests: follow/unfollow
    # ====================================================================

    def test_follow_topic(self, mock_client):
        """Test follow_topic."""
        mock_client._client.put.return_value = {}

        result = mock_client.follow_topic(tid=1)

        mock_client._client.put.assert_called_once_with("/api/v3/topics/1/follow", data={})
        assert result == {}

    def test_unfollow_topic(self, mock_client):
        """Test unfollow_topic."""
        mock_client._client.delete.return_value = {}

        result = mock_client.unfollow_topic(tid=1)

        mock_client._client.delete.assert_called_once_with("/api/v3/topics/1/follow")
        assert result == {}

    # ====================================================================
    # Tests: mark read/unread
    # ====================================================================

    def test_mark_topic_read(self, mock_client):
        """Test mark_topic_read."""
        mock_client._client.put.return_value = {}

        result = mock_client.mark_topic_read(tid=1)

        mock_client._client.put.assert_called_once_with("/api/v3/topics/1/read", data={})
        assert result == {}

    def test_mark_topic_unread(self, mock_client):
        """Test mark_topic_unread."""
        mock_client._client.delete.return_value = {}

        result = mock_client.mark_topic_unread(tid=1)

        mock_client._client.delete.assert_called_once_with("/api/v3/topics/1/read")
        assert result == {}


class TestWriteAPIDocCoverage:
    """Verify all methods have docstrings and type hints."""

    @pytest.fixture
    def write_api(self):
        """Create WriteAPI instance for testing."""
        config = NodeBBConfig(base_url="https://test.com", user_token="token")
        mock_http = MagicMock()
        return WriteAPI(mock_http, config)

    def test_all_methods_have_docstrings(self, write_api):
        """Verify all public methods have docstrings."""
        methods = [
            write_api.create_topic,
            write_api.create_reply,
            write_api.edit_post,
            write_api.delete_post,
            write_api.delete_topic,
            write_api.vote_post,
            write_api.unvote_post,
            write_api.bookmark_post,
            write_api.unbookmark_post,
            write_api.follow_topic,
            write_api.unfollow_topic,
            write_api.mark_topic_read,
            write_api.mark_topic_unread,
        ]

        for method in methods:
            assert method.__doc__ is not None, f"Missing docstring: {method.__name__}"
