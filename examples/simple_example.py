#!/usr/bin/env python3
"""
Simple example demonstrating .env configuration and automatic login.

Setup:
1. Copy .env.example to .env
2. Fill in your credentials:
   NODEBB_BASE_URL=http://your-forum.com
   NODEBB_USERNAME=your_username
   NODEBB_PASSWORD=your_password
3. Run this script: python examples/simple_example.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nodebb import NodeBBClient, NodeBBConfig

def main():
    """Main example function."""
    print("=" * 70)
    print("NodeBB Python Client - Simple Example")
    print("=" * 70)

    # Load configuration from .env file
    # This will automatically read NODEBB_BASE_URL, NODEBB_USERNAME, NODEBB_PASSWORD
    print("\n1. Loading configuration from .env file...")
    config = NodeBBConfig.from_env()
    print(f"   ✓ Base URL: {config.base_url}")
    print(f"   ✓ Username: {config.username}")
    print(f"   ✓ Password: {'***' if config.password else 'not set'}")

    # Create client - it will automatically login if credentials are provided
    print("\n2. Creating client (auto-login enabled)...")
    with NodeBBClient(config) as client:
        print("   ✓ Client created and logged in")

        # Get forum configuration
        print("\n3. Getting forum configuration...")
        forum_config = client.get_config()
        print(f"   ✓ Site title: {forum_config.get('siteTitle', 'N/A')}")
        print(f"   ✓ Min title length: {forum_config.get('minimumTitleLength', 'N/A')}")

        # Get categories
        print("\n4. Getting categories...")
        categories = client.get_categories()
        cats = categories.get('categories', [])
        print(f"   ✓ Found {len(cats)} categories:")
        for cat in cats[:5]:
            print(f"      • {cat.get('name', 'N/A')} (CID: {cat.get('cid')})")

        # Get current user info
        if config.username:
            print(f"\n5. Getting user profile...")
            user = client.get_user_by_username(userslug=config.username)
            print(f"   ✓ Username: {user.get('username')}")
            print(f"   ✓ UID: {user.get('uid')}")
            print(f"   ✓ Post count: {user.get('postcount', 0)}")
            print(f"   ✓ Reputation: {user.get('reputation', 0)}")

        # Try to create a topic (if user has permission)
        print("\n6. Attempting to create a topic...")
        try:
            topic = client.create_topic(
                cid=1,
                title="Test Topic from Python Client",
                content="This is a test topic created using the NodeBB Python client.\n\n"
                        "The client was configured using .env file and automatically logged in.",
                tags=["test", "python"],
            )
            print(f"   ✓ Topic created successfully!")
            print(f"      • TID: {topic.get('tid')}")
            print(f"      • PID: {topic.get('pid')}")
            print(f"      • Slug: {topic.get('slug')}")
        except Exception as e:
            print(f"   ✗ Failed to create topic: {e}")
            print(f"      (This is normal for new users without posting privileges)")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"\n✗ Configuration Error: {e}")
        print("\nPlease ensure:")
        print("1. You have copied .env.example to .env")
        print("2. You have filled in NODEBB_BASE_URL, NODEBB_USERNAME, NODEBB_PASSWORD")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
