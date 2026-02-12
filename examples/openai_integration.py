"""
OpenAI Function Calling integration example for NodeBB Python Client.

Demonstrates how to use NodeBB tools with OpenAI's function calling API.
"""

import json
import os
from typing import List, Any

# Check if openai is available
try:
    import openai
except ImportError:
    print("This example requires the OpenAI Python package:")
    print("  pip install openai")
    exit(1)

from nodebb import NodeBBClient, NodeBBConfig
from nodebb.tools import get_tool_definitions, execute_tool, ToolExecutor


def create_openai_client() -> openai.OpenAI:
    """Create and configure OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable not set")
        exit(1)

    return openai.OpenAI(api_key=api_key)


def run_assistant():
    """Run an interactive assistant with NodeBB tools."""
    # Initialize NodeBB client
    try:
        config = NodeBBConfig.from_env()
    except ValueError as e:
        print(f"NodeBB configuration error: {e}")
        print("\nPlease set these environment variables:")
        print("  NODEBB_BASE_URL=https://your-forum.com")
        print("  NODEBB_USER_TOKEN=your_token_here")
        return

    nodebb_client = NodeBBClient(config)

    # Get tool definitions
    tools = get_tool_definitions()
    tool_executor = ToolExecutor(nodebb_client)

    # Create OpenAI client
    openai_client = create_openai_client()

    print("=== NodeBB AI Assistant ===")
    print(f"Connected to: {config.base_url}")
    print(f"Available tools: {len(tools)}")
    print("Type 'quit' to exit\n")

    # System message
    system_prompt = f"""You are a helpful assistant for the NodeBB forum at {config.base_url}.

You can help users with:
- Reading notifications, topics, posts, categories
- Creating new topics and replies
- Editing and deleting content
- Voting and bookmarking
- Managing chat rooms
- Uploading images

When a user asks about forum activity, use the available tools to retrieve information.
When a user wants to post or modify content, ask for confirmation first for important actions.

Be concise and helpful. If you don't have enough information, say so.
"""

    # Conversation history
    messages: List[dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})

            # Call OpenAI API
            print("AI: ", end="", flush=True)

            response = openai_client.chat.completions.create(
                model="gpt-4",  # or "gpt-3.5-turbo"
                messages=messages,
                tools=tools,
                tool_choice="auto",  # Let AI decide when to use tools
            )

            # Process response
            assistant_message = response.choices[0].message

            # Check for tool calls
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function = tool_call.function
                    arguments = json.loads(function.arguments)

                    print(f"[Calling: {function.name}]")

                    # Execute the tool
                    try:
                        result = execute_tool(nodebb_client, function.name, arguments)

                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })

                        # Show result summary
                        if isinstance(result, dict):
                            if "tid" in result:
                                print(f"  -> Created topic {result['tid']}")
                            elif "pid" in result:
                                print(f"  -> Created post {result['pid']}")
                            elif "notifications" in result:
                                count = len(result.get("notifications", []))
                                print(f"  -> Found {count} notifications")
                            else:
                                print(f"  -> Success")

                    except Exception as e:
                        print(f"  -> Error: {e}")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": str(e)})
                        })

            else:
                # Regular text response
                content = assistant_message.content or ""
                print(content)

                # Add assistant response to conversation
                messages.append({
                    "role": "assistant",
                    "content": content
                })

        except KeyboardInterrupt:
            print("\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            break


def run_single_query():
    """Run a single query without conversation."""
    # Initialize NodeBB client
    try:
        config = NodeBBConfig.from_env()
    except ValueError as e:
        print(f"NodeBB configuration error: {e}")
        return

    nodebb_client = NodeBBClient(config)

    # Get tool definitions
    tools = get_tool_definitions()

    # Create OpenAI client
    openai_client = create_openai_client()

    # Example queries to test
    test_queries = [
        "What are my unread notifications?",
        "Show me the recent posts from the last week",
        "Get the list of categories",
        "Create a new topic in category 1 with title 'Test from AI'",
        "Reply to topic 123 with 'This is an automated reply'",
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")

        messages = [
            {"role": "system", "content": "You are a helpful assistant. Use the available tools to help with the user's request."}
        ]

        user_message = {"role": "user", "content": query}
        messages.append(user_message)

        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
        )

        assistant_message = response.choices[0].message

        # Display response
        print("Response:")
        if assistant_message.content:
            print(assistant_message.content)

        # Handle tool calls
        if assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                function = tool_call.function
                arguments = json.loads(function.arguments)

                tool_name = function.name
                print(f"\nTool: {tool_name}")
                print(f"Arguments: {json.dumps(arguments, indent=2)}")

                # Execute the tool
                result = execute_tool(nodebb_client, tool_name, arguments)

                # Show result
                print(f"Result:")
                print(json.dumps(result, indent=2))


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "interactive":
            run_assistant()
        elif mode == "query":
            run_single_query()
        else:
            print(f"Unknown mode: {mode}")
            print("\nUsage:")
            print("  python openai_integration.py interactive  # Run interactive assistant")
            print("  python openai_integration.py query       # Run test queries")
    else:
        print("Please specify a mode:")
        print("  python openai_integration.py interactive")
        print("  python openai_integration.py query")


if __name__ == "__main__":
    main()
