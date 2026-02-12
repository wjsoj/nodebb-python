# NodeBB Python Client

Python client for [NodeBB](https://github.com/NodeBB/NodeBB) Forum API with OpenAI Function Calling support.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/release/python-3.10.0/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Installation

```bash
pip install nodebb-python-client
```

Or install from source:

```bash
git clone https://github.com/NodeBB/NodeBB.git
cd NodeBB/python_client
pip install -e .
```

## Quick Start

```python
from nodebb import NodeBBClient, NodeBBConfig

# Configure from environment variables
config = NodeBBConfig.from_env()

with NodeBBClient(config) as client:
    # Get notifications
    notifications = client.get_notifications()

    # Create a topic
    topic = client.create_topic(
        cid=1,
        title="Hello from Python",
        content="Posted using NodeBB Python client"
    )

    # Send a chat message
    client.send_chat_message(room_id=1, message="Hello!")
```

## Configuration

Create a `.env` file:

```bash
NODEBB_BASE_URL="https://your-forum.com"
NODEBB_USERNAME="your_username"
NODEBB_PASSWORD="your_password"
```

Or configure programmatically:

```python
config = NodeBBConfig(
    base_url="https://your-forum.com",
    username="your_username",
    password="your_password"
)
```

### Authentication Methods

| Method | Use Case |
|--------|----------|
| Username/Password | Recommended. Auto-login with session management |
| User Token | Pre-generated bearer token for specific user |
| Master Token | Admin token with `_uid` parameter for impersonation |

## API Reference

### Read API

```python
# Notifications
client.get_notifications(filter="", page=1)
client.get_unread_count()
client.get_unread_topics(start=0, per_page=20, filter="")

# Content
client.get_topic(tid=1)
client.get_categories()
client.get_category(cid=1)
client.get_post(pid=1)
client.get_recent_posts(term="week")  # all, day, week, month

# Users
client.get_user(uid=1)
client.get_user_by_username(userslug="admin")
client.search_users(query="john")
client.get_config()
```

### Write API

```python
# Topics and Posts
client.create_topic(cid=1, title="Title", content="Content", tags=["tag1"])
client.create_reply(tid=1, content="Reply content")
client.edit_post(pid=1, content="New content")
client.delete_post(pid=1)
client.delete_topic(tid=1)

# Voting and Bookmarks
client.vote_post(pid=1, delta=1)   # +1 upvote, -1 downvote
client.bookmark_post(pid=1)

# Following
client.follow_topic(tid=1)
client.mark_topic_read(tid=1)
```

### Chat API

```python
# Chat Rooms
client.get_chats()
client.create_chat_room(uids=[1, 2])
client.get_chat_room_detail(room_id=1)

# Messages
client.get_chat_messages(room_id=1, count=20)
client.send_chat_message(room_id=1, message="Hello")
client.leave_chat_room(room_id=1)
```

### Upload API

```python
client.upload_image(file_path="/path/to/image.png")
client.upload_file(file_path="/path/to/file.pdf")
```

## OpenAI Function Calling

The client provides 46 pre-defined tools compatible with OpenAI's Function Calling API:

```python
from nodebb.tools import get_tool_definitions, execute_tool

# Get tool definitions
tools = get_tool_definitions()

# Execute a tool
result = execute_tool(client, "get_notifications", {"filter": "mention"})
```

### Integration Example

```python
import openai
from nodebb import NodeBBClient, NodeBBConfig
from nodebb.tools import get_tool_definitions, execute_tool

config = NodeBBConfig.from_env()
client = NodeBBClient(config)
tools = get_tool_definitions()

openai_client = openai.OpenAI()

response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Get my unread notifications"}],
    tools=tools,
)

# Handle tool calls
for tool_call in response.choices[0].message.tool_calls:
    result = execute_tool(
        client,
        tool_call.function.name,
        json.loads(tool_call.function.arguments)
    )
```

## Error Handling

```python
from nodebb.exceptions import (
    NodeBBError,
    AuthenticationError,
    PrivilegeError,
    ResourceNotFoundError,
    RateLimitError,
)

try:
    client.delete_topic(tid=123)
except AuthenticationError:
    print("Invalid credentials")
except PrivilegeError:
    print("Permission denied")
except ResourceNotFoundError:
    print("Topic not found")
except NodeBBError as e:
    print(f"Error: {e}")
```

## Project Structure

```
python_client/
├── nodebb/
│   ├── __init__.py
│   ├── client.py          # Main client
│   ├── config.py          # Configuration
│   ├── exceptions.py      # Exception classes
│   ├── tools.py           # OpenAI tools
│   └── api/
│       ├── read.py        # GET endpoints
│       ├── write.py       # POST/PUT/DELETE
│       ├── chat.py        # Chat API
│       ├── upload.py      # File uploads
│       └── auth.py        # Authentication
├── tests/
│   ├── test_read_api.py
│   ├── test_write_api.py
│   └── test_integration.py
├── examples/
│   ├── basic_usage.py
│   ├── simple_example.py
│   └── openai_integration.py
├── pyproject.toml
├── requirements.txt
├── .env.example
└── LICENSE
```

## Testing

```bash
# Unit tests
uv run pytest tests/ -v

# Integration tests (requires .env with credentials)
uv run pytest tests/test_integration.py -v

# With coverage
uv run pytest tests/ --cov=nodebb
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run linter
uv run ruff check nodebb/

# Format code
uv run black nodebb/

# Type check
uv run mypy nodebb/
```

## API Coverage

| Category | Endpoints |
|----------|-----------|
| Read API | notifications, unread, topics, categories, users, config |
| Write API | create/edit/delete topics and posts, vote, bookmark, follow |
| Chat API | rooms, messages, users management |
| Upload API | image and file uploads |

## License

MIT License. See [LICENSE](LICENSE) for details.

## Links

- [NodeBB Documentation](https://docs.nodebb.org/)
- [NodeBB Community](https://community.nodebb.org/)
- [GitHub Issues](https://github.com/NodeBB/NodeBB/issues)
