"""
Basic usage examples for NodeBB Python Client.

Demonstrates common patterns for using the client.
"""

import os
from nodebb import NodeBBClient, NodeBBConfig


def example_with_user_token():
    """Example using user token authentication."""
    print("=== Example: User Token Authentication ===")

    config = NodeBBConfig.for_user_token(
        base_url="https://your-nodebb.com",
        token="your_user_token_here"
    )

    with NodeBBClient(config) as client:
        # Get notifications
        print("Getting notifications...")
        notifications = client.get_notifications(filter="new-mention")
        print(f"Found {len(notifications.get('notifications', []))} mentions")

        # Get unread count
        print("\nGetting unread count...")
        count = client.get_unread_count()
        print(f"Unread topics: {count}")

        # Get categories
        print("\nGetting categories...")
        categories = client.get_categories()
        for cat in categories.get("categories", [])[:5]:
            print(f"  - {cat.get('name', 'Unknown')} (CID: {cat.get('cid', 'N/A')})")


def example_with_master_token():
    """Example using master token authentication."""
    print("=== Example: Master Token Authentication ===")

    config = NodeBBConfig.for_master_token(
        base_url="https://your-nodebb.com",
        token="your_master_token_here",
        uid=123,  # User ID to act as
    )

    with NodeBBClient(config) as client:
        # Create a topic as the user
        print("Creating topic...")
        result = client.create_topic(
            cid=1,
            title="Posted via Master Token",
            content="This topic was created using master token authentication."
        )
        print(f"Created topic TID: {result.get('tid')}")

        # Reply to a topic
        print("\nReplying to topic...")
        reply = client.create_reply(
            tid=result.get("tid", 1),
            content="This is a reply via master token."
        )
        print(f"Created reply PID: {reply.get('pid')}")


def example_from_environment():
    """Example loading configuration from environment variables."""
    print("=== Example: Environment Variables ===")

    # Set environment variables first:
    # export NODEBB_BASE_URL="https://your-nodebb.com"
    # export NODEBB_USER_TOKEN="your_token"

    try:
        config = NodeBBConfig.from_env()
        print(f"Loaded config for: {config.base_url}")
        print(f"Auth type: {config.auth_type}")

        with NodeBBClient(config) as client:
            # Get forum config
            print("\nGetting forum config...")
            forum_config = client.get_config()

            print(f"Minimum title length: {forum_config.get('minimumTitleLength', 'N/A')}")
            print(f"Maximum title length: {forum_config.get('maximumTitleLength', 'N/A')}")
            print(f"Minimum post length: {forum_config.get('minimumPostLength', 'N/A')}")
            print(f"Maximum post length: {forum_config.get('maximumPostLength', 'N/A')}")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nHint: Set NODEBB_BASE_URL environment variable")


def example_pagination():
    """Example of paginated requests."""
    print("=== Example: Pagination ===")

    config = NodeBBConfig.from_env()
    with NodeBBClient(config) as client:
        # Get first page of unread topics
        print("Getting first page...")
        page1 = client.get_unread_topics(start=0, per_page=10)
        print(f"Page 1: {len(page1.get('topics', []))} topics")

        # Get second page
        if page1.get("nextStart"):
            print("\nGetting second page...")
            page2 = client.get_unread_topics(
                start=page1["nextStart"], per_page=10
            )
            print(f"Page 2: {len(page2.get('topics', []))} topics")


def example_search_and_browse():
    """Example of searching and browsing content."""
    print("=== Example: Search and Browse ===")

    config = NodeBBConfig.from_env()
    with NodeBBClient(config) as client:
        # Search for users
        print("Searching for users...")
        users = client.search_users(query="john", section="joindate")
        print(f"Found {users.get('userCount', 0)} users")

        # Get specific category
        print("\nGetting category...")
        category = client.get_category(cid=1)
        print(f"Category: {category.get('name', 'Unknown')}")
        print(f"Topics in category: {len(category.get('topics', []))}")

        # Get specific topic
        if category.get("topics"):
            first_topic = category["topics"][0]
            print(f"\nGetting topic: {first_topic.get('title', 'N/A')}")
            topic = client.get_topic(tid=first_topic.get("tid"))
            print(f"Posts in topic: {len(topic.get('posts', []))}")


def example_interactive_operations():
    """Example of interactive write operations."""
    print("=== Example: Interactive Operations ===")

    config = NodeBBConfig.from_env()
    with NodeBBClient(config) as client:
        # Vote on a post
        print("Voting on post...")
        try:
            client.vote_post(pid=123, delta=1)
            print("Upvoted post 123")
        except Exception as e:
            print(f"Vote failed: {e}")

        # Bookmark a post
        print("\nBookmarking post...")
        try:
            client.bookmark_post(pid=123)
            print("Bookmarked post 123")
        except Exception as e:
            print(f"Bookmark failed: {e}")

        # Follow a topic
        print("\nFollowing topic...")
        try:
            client.follow_topic(tid=456)
            print("Following topic 456")
        except Exception as e:
            print(f"Follow failed: {e}")


def example_error_handling():
    """Example of proper error handling."""
    print("=== Example: Error Handling ===")

    from nodebb.exceptions import (
        AuthenticationError,
        PrivilegeError,
        ResourceNotFoundError,
        NodeBBError,
    )

    config = NodeBBConfig.from_env()
    with NodeBBClient(config) as client:
        # Try to access protected endpoint
        print("Attempting protected operation...")

        try:
            result = client.create_topic(
                cid=1,
                title="Test Topic",
                content="Test content"
            )
            print(f"Success! Created topic {result.get('tid')}")
        except AuthenticationError:
            print("Error: Invalid or missing authentication token")
            print("Please check your NODEBB_USER_TOKEN environment variable")
        except PrivilegeError as e:
            print(f"Error: Insufficient privileges - {e}")
            print("You may not have permission to post in this category")
        except ResourceNotFoundError:
            print("Error: Category not found")
        except NodeBBError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import sys

    # Check if config is available
    if os.getenv("NODEBB_BASE_URL"):
        # Run the requested example
        if len(sys.argv) > 1:
            example = sys.argv[1]
            examples = {
                "user_token": example_with_user_token,
                "master_token": example_with_master_token,
                "environment": example_from_environment,
                "pagination": example_pagination,
                "search": example_search_and_browse,
                "interactive": example_interactive_operations,
                "errors": example_error_handling,
            }

            if example in examples:
                examples[example]()
            else:
                print(f"Unknown example: {example}")
                print("\nAvailable examples:")
                for name in examples.keys():
                    print(f"  - {name}")
        else:
            print("Please specify an example:")
            print("  python basic_usage.py <example_name>")
            print("\nAvailable examples:")
            print("  - user_token")
            print("  - master_token")
            print("  - environment")
            print("  - pagination")
            print("  - search")
            print("  - interactive")
            print("  - errors")
    else:
        print("NODEBB_BASE_URL environment variable not set")
        print("\nSet it with:")
        print("  export NODEBB_BASE_URL='https://your-nodebb.com'")
        print("  export NODEBB_USER_TOKEN='your_token'")
