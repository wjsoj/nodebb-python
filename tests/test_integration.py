"""
Integration tests for NodeBB Python Client.

Tests the complete workflow:
1. Login with username/password
2. Get unread topics and find the latest post
3. Get unread notifications
4. Reply to all unread posts
5. Reply to all unread private chat messages

Note: These tests make actual API calls and require a running NodeBB instance.
Set environment variables in .env file before running.

Usage:
    # Run all integration tests
    uv run pytest tests/test_integration.py -v -s

    # Run specific test
    uv run pytest tests/test_integration.py::TestIntegration::test_login -v -s

    # Run with markers
    uv run pytest tests/test_integration.py -v -s -m integration
"""

from __future__ import annotations

import os
import re
import time
from datetime import datetime
from typing import Any, Dict, List

import pytest

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from nodebb import NodeBBClient, NodeBBConfig
from nodebb.exceptions import NodeBBError, PrivilegeError


# Marker for integration tests
pytestmark = pytest.mark.integration


def check_env_vars():
    """Check if required environment variables are set."""
    required = ["NODEBB_BASE_URL", "NODEBB_USERNAME", "NODEBB_PASSWORD"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        pytest.skip(f"Missing environment variables: {missing}")


class TestIntegration:
    """Integration tests for complete workflow."""

    @pytest.fixture(scope="class")
    def config(self):
        """Create configuration from environment."""
        check_env_vars()
        return NodeBBConfig.from_env()

    @pytest.fixture(scope="class")
    def client(self, config):
        """Create and login client."""
        with NodeBBClient(config) as client:
            yield client

    # ========================================================================
    # Test 1: Login
    # ========================================================================

    def test_login(self, config):
        """Test login with username and password."""
        print("\n" + "=" * 70)
        print("TEST 1: Login with username/password")
        print("=" * 70)

        print(f"  Base URL: {config.base_url}")
        print(f"  Username: {config.username}")

        with NodeBBClient(config) as client:
            # Verify login by getting config
            forum_config = client.get_config()
            print(f"  Site Title: {forum_config.get('siteTitle', 'N/A')}")

            # Get current user info
            user = client.get_user_by_username(userslug=config.username)
            print(f"  User ID: {user.get('uid')}")
            print(f"  Display Name: {user.get('displayname')}")
            print(f"  Post Count: {user.get('postcount')}")

            assert user.get("username") == config.username
            print("\n  ✅ Login successful!")

    # ========================================================================
    # Test 2: Get Unread Topics
    # ========================================================================

    def test_get_unread_topics(self, client):
        """Test getting unread topics and finding the latest post."""
        print("\n" + "=" * 70)
        print("TEST 2: Get Unread Topics")
        print("=" * 70)

        # Get unread count first
        unread_count = client.get_unread_count()
        print(f"  Unread topic count: {unread_count}")

        # Get unread topics with all filters
        for filter_type in ["", "new", "watched", "unreplied"]:
            result = client.get_unread_topics(filter=filter_type)
            topics = result.get("topics", [])
            count = result.get("topicCount", 0)
            filter_name = filter_type if filter_type else "all"
            print(f"  Filter '{filter_name}': {count} topics")

        # Get detailed info for unread topics
        result = client.get_unread_topics()
        topics = result.get("topics", [])

        if topics:
            print(f"\n  📚 Found {len(topics)} unread topics:")
            for i, topic in enumerate(topics[:5], 1):
                print(f"\n  {i}. 【{topic.get('title')}】")
                print(f"     TID: {topic.get('tid')}")
                print(f"     Author: {topic.get('user', {}).get('username')}")
                print(f"     Category: {topic.get('category', {}).get('name')}")
                print(f"     Replies: {topic.get('postcount', 0)}")
                print(f"     Time: {topic.get('timestampISO')}")

                # Get latest post from teaser
                teaser = topic.get("teaser")
                if teaser:
                    print(f"     Latest Post PID: {teaser.get('pid')}")
                    content = teaser.get("content", "")[:100].replace("\n", " ")
                    print(f"     Preview: {content}...")
        else:
            print("\n  📭 No unread topics found")

        print("\n  ✅ Get unread topics successful!")

    # ========================================================================
    # Test 3: Get Unread Notifications
    # ========================================================================

    def test_get_unread_notifications(self, client):
        """Test getting all unread notifications."""
        print("\n" + "=" * 70)
        print("TEST 3: Get Unread Notifications")
        print("=" * 70)

        # Get all notifications
        result = client.get_notifications()
        notifications = result.get("notifications", [])

        # Count unread
        unread_notifs = [n for n in notifications if not n.get("read", True)]
        print(f"  Total notifications: {len(notifications)}")
        print(f"  Unread notifications: {len(unread_notifs)}")

        # Group by type
        type_counts = {}
        for n in notifications:
            t = n.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        print(f"  Type distribution: {type_counts}")

        # Show available filters
        filters = result.get("filters", [])
        print(f"\n  Available filters:")
        for f in filters[:6]:
            name = f.get("name", "")
            count = f.get("count", "")
            if count:
                print(f"    - {name}: {count}")
            else:
                print(f"    - {name}")

        if notifications:
            print(f"\n  🔔 Recent notifications:")
            for i, notif in enumerate(notifications[:5], 1):
                # Clean HTML from body
                body = re.sub(r"<[^>]+>", "", notif.get("bodyShort", ""))
                read_status = "✅" if notif.get("read") else "🆕"
                print(f"\n  {i}. [{notif.get('type')}] {read_status}")
                print(f"     {body}")
                print(f"     From: {notif.get('user', {}).get('username')}")
                print(f"     Path: {notif.get('path')}")
                print(f"     Time: {notif.get('datetimeISO')}")
        else:
            print("\n  📭 No notifications found")

        print("\n  ✅ Get notifications successful!")

    # ========================================================================
    # Test 4: Reply to Unread Posts
    # ========================================================================

    def test_reply_to_unread_posts(self, client):
        """Test replying to all unread posts."""
        print("\n" + "=" * 70)
        print("TEST 4: Reply to Unread Posts")
        print("=" * 70)

        # Get unread topics
        result = client.get_unread_topics()
        topics = result.get("topics", [])

        if not topics:
            print("  📭 No unread topics to reply to")
            print("\n  ✅ Test skipped (no unread posts)")
            return

        replies_sent = 0
        errors = []

        for topic in topics[:3]:  # Limit to first 3 to avoid spam
            tid = topic.get("tid")
            title = topic.get("title", "Unknown")

            print(f"\n  📝 Replying to topic: {title} (TID: {tid})")

            try:
                # Create a reply
                reply_content = (
                    f"This is an automated test reply.\n\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"Replying to: {title}"
                )

                reply = client.create_reply(
                    tid=tid,
                    content=reply_content,
                )

                pid = reply.get("pid")
                print(f"     ✅ Reply sent! PID: {pid}")
                replies_sent += 1

                # Mark topic as read (optional, may fail without permission)
                try:
                    client.mark_topic_read(tid=tid)
                    print(f"     ✅ Marked as read")
                except (PrivilegeError, NodeBBError) as e:
                    print(f"     ⚠️ Could not mark as read: {e}")

                # Wait a bit to avoid rate limiting
                time.sleep(1)

            except PrivilegeError as e:
                error_msg = f"Permission denied for topic {tid}: {e}"
                print(f"     ⚠️ {error_msg}")
                errors.append(error_msg)
            except NodeBBError as e:
                error_msg = f"Error replying to topic {tid}: {e}"
                print(f"     ❌ {error_msg}")
                errors.append(error_msg)

        print(f"\n  📊 Summary:")
        print(f"     Topics processed: {min(len(topics), 3)}")
        print(f"     Replies sent: {replies_sent}")
        print(f"     Errors: {len(errors)}")

        if errors:
            print(f"\n  ⚠️ Some errors occurred:")
            for err in errors:
                print(f"     - {err}")

        print("\n  ✅ Reply to unread posts test completed!")

    # ========================================================================
    # Test 5: Reply to Private Chat Messages
    # ========================================================================

    def test_reply_to_chat_messages(self, client):
        """Test replying to unread private chat messages."""
        print("\n" + "=" * 70)
        print("TEST 5: Reply to Private Chat Messages")
        print("=" * 70)

        # Get chat rooms
        chats_result = client.get_chats()
        rooms = chats_result.get("rooms", [])

        if not rooms:
            print("  📭 No chat rooms found")
            print("\n  ✅ Test skipped (no chat rooms)")
            return

        print(f"  Found {len(rooms)} chat rooms")

        # Find rooms with unread messages
        unread_rooms = [r for r in rooms if r.get("unread", False)]
        print(f"  Rooms with unread messages: {len(unread_rooms)}")

        messages_sent = 0
        errors = []

        for room in unread_rooms[:3]:  # Limit to first 3
            room_id = room.get("roomId")

            # Get room details
            try:
                room_detail = client.get_chat_room_detail(room_id)
                users = room_detail.get("users", [])
                user_names = [u.get("username") for u in users]
                print(f"\n  💬 Chat Room {room_id}")
                print(f"     Participants: {', '.join(user_names)}")
            except Exception as e:
                print(f"\n  💬 Chat Room {room_id}")
                print(f"     (Could not get details: {e})")

            # Get recent messages
            try:
                messages_result = client.get_chat_messages(room_id=room_id, count=5)
                messages = messages_result.get("messages", [])

                if messages:
                    print(f"     Recent messages: {len(messages)}")
                    for msg in messages[-2:]:
                        sender = msg.get("fromUser", {}).get("username", "Unknown")
                        content = msg.get("content", "")[:50].replace("\n", " ")
                        print(f"       - {sender}: {content}...")

            except Exception as e:
                print(f"     Could not get messages: {e}")

            # Send a reply
            try:
                reply_message = (
                    f"Hello! This is an automated test reply.\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                result = client.send_chat_message(
                    room_id=room_id,
                    message=reply_message,
                )

                mid = result.get("mid") or result.get("payload", {}).get("mid")
                print(f"     ✅ Message sent! MID: {mid}")
                messages_sent += 1

                # Wait a bit to avoid rate limiting
                time.sleep(1)

            except PrivilegeError as e:
                error_msg = f"Permission denied for room {room_id}: {e}"
                print(f"     ⚠️ {error_msg}")
                errors.append(error_msg)
            except NodeBBError as e:
                error_msg = f"Error sending message to room {room_id}: {e}"
                print(f"     ❌ {error_msg}")
                errors.append(error_msg)

        # If no unread rooms, try to send to first room as test
        if not unread_rooms and rooms:
            print("\n  No unread rooms. Testing send to first room...")
            room_id = rooms[0].get("roomId")
            try:
                test_message = f"Test message at {datetime.now().strftime('%H:%M:%S')}"
                result = client.send_chat_message(room_id=room_id, message=test_message)
                print(f"     ✅ Test message sent to room {room_id}")
                messages_sent += 1
            except Exception as e:
                print(f"     ❌ Failed to send test message: {e}")

        print(f"\n  📊 Summary:")
        print(f"     Rooms processed: {min(len(unread_rooms) if unread_rooms else 1, 3)}")
        print(f"     Messages sent: {messages_sent}")
        print(f"     Errors: {len(errors)}")

        print("\n  ✅ Reply to chat messages test completed!")

    # ========================================================================
    # Test 6: Full Workflow (Combined)
    # ========================================================================

    def test_full_workflow(self, client):
        """Test the complete workflow in one test."""
        print("\n" + "=" * 70)
        print("TEST 6: Full Workflow Summary")
        print("=" * 70)

        # Get forum updates
        from nodebb.tools import get_forum_updates

        updates = get_forum_updates(client)
        print(updates["summary"])

        print("\n  ✅ Full workflow test completed!")


class TestNotificationFilters:
    """Test various notification filters."""

    @pytest.fixture(scope="class")
    def client(self):
        """Create and login client."""
        check_env_vars()
        config = NodeBBConfig.from_env()
        with NodeBBClient(config) as client:
            yield client

    def test_notification_filter_all(self, client):
        """Test getting all notifications."""
        result = client.get_notifications(filter="")
        assert "notifications" in result
        print(f"\n  All notifications: {len(result.get('notifications', []))}")

    def test_notification_filter_replies(self, client):
        """Test filtering by replies."""
        result = client.get_notifications(filter="new-reply")
        assert "notifications" in result
        print(f"  Reply notifications: {len(result.get('notifications', []))}")

    def test_notification_filter_chat(self, client):
        """Test filtering by chat."""
        result = client.get_notifications(filter="new-chat")
        assert "notifications" in result
        print(f"  Chat notifications: {len(result.get('notifications', []))}")

    def test_notification_filter_mentions(self, client):
        """Test filtering by mentions."""
        result = client.get_notifications(filter="mention")
        assert "notifications" in result
        print(f"  Mention notifications: {len(result.get('notifications', []))}")


class TestUnreadTopicFilters:
    """Test various unread topic filters."""

    @pytest.fixture(scope="class")
    def client(self):
        """Create and login client."""
        check_env_vars()
        config = NodeBBConfig.from_env()
        with NodeBBClient(config) as client:
            yield client

    def test_unread_filter_all(self, client):
        """Test getting all unread topics."""
        result = client.get_unread_topics(filter="")
        assert "topics" in result
        print(f"\n  All unread: {result.get('topicCount', 0)}")

    def test_unread_filter_new(self, client):
        """Test filtering by new topics."""
        result = client.get_unread_topics(filter="new")
        assert "topics" in result
        print(f"  New topics: {result.get('topicCount', 0)}")

    def test_unread_filter_watched(self, client):
        """Test filtering by watched topics."""
        result = client.get_unread_topics(filter="watched")
        assert "topics" in result
        print(f"  Watched topics: {result.get('topicCount', 0)}")

    def test_unread_filter_unreplied(self, client):
        """Test filtering by unreplied topics."""
        result = client.get_unread_topics(filter="unreplied")
        assert "topics" in result
        print(f"  Unreplied topics: {result.get('topicCount', 0)}")


# ============================================================================
# Standalone runner
# ============================================================================

if __name__ == "__main__":
    """Run tests directly without pytest."""
    import sys

    print("=" * 70)
    print("NodeBB Python Client - Integration Tests")
    print("=" * 70)

    # Check environment
    check_env_vars()

    # Create config and client
    config = NodeBBConfig.from_env()
    print(f"\nConnecting to: {config.base_url}")
    print(f"Username: {config.username}")

    try:
        with NodeBBClient(config) as client:
            test = TestIntegration()

            # Run each test
            print("\n" + "=" * 70)
            print("Running integration tests...")
            print("=" * 70)

            try:
                test.test_get_unread_topics(client)
            except Exception as e:
                print(f"  ❌ Test failed: {e}")

            try:
                test.test_get_unread_notifications(client)
            except Exception as e:
                print(f"  ❌ Test failed: {e}")

            try:
                test.test_reply_to_unread_posts(client)
            except Exception as e:
                print(f"  ❌ Test failed: {e}")

            try:
                test.test_reply_to_chat_messages(client)
            except Exception as e:
                print(f"  ❌ Test failed: {e}")

            try:
                test.test_full_workflow(client)
            except Exception as e:
                print(f"  ❌ Test failed: {e}")

            print("\n" + "=" * 70)
            print("All tests completed!")
            print("=" * 70)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
