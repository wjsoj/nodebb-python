"""
OpenAI Function Calling tools module for NodeBB.

Provides tool definitions in OpenAI's function calling format and
execution methods that map to client API calls.
"""

from __future__ import annotations

from typing import Any, Dict, Callable, List, Optional

from nodebb.client import NodeBBClient


def get_tool_definitions() -> List[Dict[str, Any]]:
    """Get all tool definitions in OpenAI Function Calling format.

    Returns a list of tool definitions compatible with OpenAI's function
    calling API. Total: 46 tools covering all NodeBB API endpoints.

    Tool Categories:
        - Read API: 12 tools (notifications, unread, topics, posts, categories, users, config)
        - Write API: 12 tools (create, edit, delete, vote, bookmark, follow/unfollow, mark read/unread)
        - Topic State/Tags: 6 tools (lock/unlock, pin/unpin, update tags, add/remove tags)
        - Post Operations: 4 tools (move, restore, soft delete, get replies)
        - Chat API: 8 tools (rooms, create, send message, get messages, room detail, add/remove users, rename)
        - Upload API: 2 tools (image, file)
        - Utility: 1 tool (forum updates summary)
    """
    tools = [
        # ====================================================================
        # Read Tools (12)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "get_notifications",
                "description": (
                    "获取用户最近通知列表，包含通知类型、来源用户、内容摘要、"
                    "时间戳、相关链接等详细信息。支持按类型过滤。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": (
                                "通知类型过滤。可选值: "
                                "''(全部), 'new-topic'(新主题), 'new-reply'(新回复), "
                                "'mention'(@提及), 'new-chat'(新私信), "
                                "'new-group-chat'(群聊消息), 'follow'(新关注), "
                                "'upvote'(点赞), 'new-reward'(新奖励)"
                            ),
                            "default": "",
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码（默认1）",
                            "default": 1,
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_unread_count",
                "description": "获取未读主题数量",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_unread_topics",
                "description": (
                    "获取未读主题列表，包含主题详情、作者、分类、标签、最新回复预览等信息。"
                    "支持按类型过滤：全部、新主题、已关注、未回复"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "integer",
                            "description": "起始索引（用于分页，默认0）",
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页主题数量",
                        },
                        "filter": {
                            "type": "string",
                            "description": (
                                "主题过滤类型。可选值: "
                                "''(全部未读), 'new'(新主题), "
                                "'watched'(已关注), 'unreplied'(未回复)"
                            ),
                            "default": "",
                            "enum": ["", "new", "watched", "unreplied"],
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_recent_posts",
                "description": "获取最近发布的帖子",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "term": {
                            "type": "string",
                            "description": (
                                "时间范围过滤。可选值: "
                                "'all'(全部), 'day'(一天内), 'week'(一周内), 'month'(一月内)"
                            ),
                            "default": "all",
                            "enum": ["all", "day", "week", "month"],
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_topic",
                "description": "获取主题详情及其回复",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                        "slug": {
                            "type": "string",
                            "description": "主题别名（可选）",
                        },
                        "post_index": {
                            "type": "integer",
                            "description": "帖子索引（跳转到指定位置）",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_categories",
                "description": "获取论坛所有分类",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_category",
                "description": "获取指定分类的详情和主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cid": {
                            "type": "integer",
                            "description": "分类ID",
                        },
                        "slug": {
                            "type": "string",
                            "description": "分类别名（可选）",
                        },
                        "topic_index": {
                            "type": "integer",
                            "description": "主题索引（用于分页）",
                        },
                    },
                    "required": ["cid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_user",
                "description": "根据用户ID获取用户信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "uid": {
                            "type": "integer",
                            "description": "用户ID",
                        },
                    },
                    "required": ["uid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_by_username",
                "description": "根据用户名获取用户信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "userslug": {
                            "type": "string",
                            "description": "URL安全的用户名",
                        },
                    },
                    "required": ["userslug"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "search_users",
                "description": "搜索用户",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索关键词（空字符串表示全部用户）",
                        },
                        "section": {
                            "type": "string",
                            "description": (
                                "排序方式。可选值："
                                "'joindate'(加入时间), 'online'(在线用户), "
                                "'sort-posts'(帖子数), 'sort-reputation'(声望值), "
                                "'banned'(已封禁), 'flagged'(被举报)"
                            ),
                            "default": "joindate",
                            "enum": ["joindate", "online", "sort-posts", "sort-reputation", "banned", "flagged"],
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_config",
                "description": "获取论坛配置信息",
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_post",
                "description": "获取单个帖子的详细信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        # ====================================================================
        # Write Tools - Topics/Posts (12)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "create_topic",
                "description": "创建新主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cid": {
                            "type": "integer",
                            "description": "分类ID（要在哪个分类发帖）",
                        },
                        "title": {
                            "type": "string",
                            "description": "主题标题",
                        },
                        "content": {
                            "type": "string",
                            "description": "主题内容（支持Markdown格式）",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表（可选）",
                        },
                    },
                    "required": ["cid", "title", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_reply",
                "description": "回复主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                        "content": {
                            "type": "string",
                            "description": "回复内容（支持Markdown格式）",
                        },
                        "to_pid": {
                            "type": "integer",
                            "description": "回复的帖子ID（可选，用于引用回复）",
                        },
                    },
                    "required": ["tid", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "edit_post",
                "description": "编辑帖子",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                        "content": {
                            "type": "string",
                            "description": "新内容（支持Markdown格式）",
                        },
                        "title": {
                            "type": "string",
                            "description": "新标题（仅主贴可修改标题）",
                        },
                    },
                    "required": ["pid", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_post",
                "description": "删除帖子",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "要删除的帖子ID",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_topic",
                "description": "删除主题（会删除主题下的所有帖子）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "要删除的主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "vote_post",
                "description": "给帖子投票（点赞/点踩）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                        "delta": {
                            "type": "integer",
                            "description": "投票值（正数为点赞，负数为点踩，0为取消投票）",
                            "default": 1,
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "unvote_post",
                "description": "取消对帖子的投票",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "bookmark_post",
                "description": "收藏帖子",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "unbookmark_post",
                "description": "取消收藏帖子",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "follow_topic",
                "description": "关注主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "unfollow_topic",
                "description": "取消关注主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mark_topic_read",
                "description": "标记主题为已读",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "mark_topic_unread",
                "description": "标记主题为未读",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        # ====================================================================
        # Write Tools - Topic State, Pin, Tags (6)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "set_topic_state",
                "description": "设置主题状态（锁定/解锁）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                        "state": {
                            "type": "string",
                            "description": "状态：'locked'(锁定) 或 'unlocked'(解锁）",
                            "enum": ["locked", "unlocked"],
                        },
                    },
                    "required": ["tid", "state"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "pin_topic",
                "description": "置顶主题（显示在列表顶部）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                        "expiry": {
                            "type": "integer",
                            "description": "自动取消置顶的时间戳（UNIX时间），留空表示永久置顶",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "unpin_topic",
                "description": "取消置顶主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_topic_tags",
                "description": "更新主题的所有标签（会替换现有全部标签）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表",
                        },
                    },
                    "required": ["tid", "tags"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_topic_tag",
                "description": "为主题添加单个标签",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                        "tag": {
                            "type": "string",
                            "description": "要添加的标签内容",
                        },
                    },
                    "required": ["tid", "tag"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "remove_topic_tags",
                "description": "删除主题的所有标签",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tid": {
                            "type": "integer",
                            "description": "主题ID",
                        },
                    },
                    "required": ["tid"],
                },
            },
        },
        # ====================================================================
        # Write Tools - Post Operations (5)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "move_post",
                "description": "移动帖子到另一个主题",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "要移动的帖子ID",
                        },
                        "tid": {
                            "type": "integer",
                            "description": "目标主题ID",
                        },
                    },
                    "required": ["pid", "tid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "restore_post",
                "description": "恢复被软删除的帖子",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "要恢复的帖子ID",
                        },
                        "tid": {
                            "type": "integer",
                            "description": "目标主题ID（可选，默认恢复到原主题）",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "soft_delete_post",
                "description": "软删除帖子（管理员可恢复）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "要软删除的帖子ID",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_post_replies",
                "description": "获取帖子的直接回复列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pid": {
                            "type": "integer",
                            "description": "帖子ID",
                        },
                        "start": {
                            "type": "integer",
                            "description": "起始索引（用于分页）",
                        },
                        "direction": {
                            "type": "string",
                            "description": "排序方向：'-1'(最新优先) 或 '1'(最旧优先）",
                            "enum": ["-1", "1"],
                            "default": "-1",
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页回复数量",
                        },
                    },
                    "required": ["pid"],
                },
            },
        },
        # ====================================================================
        # Chat Tools (7)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "get_chats",
                "description": "获取聊天室列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start": {
                            "type": "integer",
                            "description": "起始索引（用于分页）",
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页聊天室数量",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "create_chat_room",
                "description": "创建聊天室",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "uids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "要添加到聊天室的用户ID列表",
                        },
                    },
                    "required": ["uids"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "send_chat_message",
                "description": "发送聊天消息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {
                            "type": "integer",
                            "description": "聊天室ID",
                        },
                        "message": {
                            "type": "string",
                            "description": "消息内容",
                        },
                    },
                    "required": ["room_id", "message"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_chat_messages",
                "description": "获取聊天室消息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {
                            "type": "integer",
                            "description": "聊天室ID",
                        },
                        "start": {
                            "type": "integer",
                            "description": "起始索引（用于分页）",
                        },
                        "count": {
                            "type": "integer",
                            "description": "获取的消息数量",
                        },
                        "uid": {
                            "type": "integer",
                            "description": "筛选特定用户的消息（可选）",
                        },
                    },
                    "required": ["room_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "rename_room",
                "description": "重命名聊天室",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {
                            "type": "integer",
                            "description": "聊天室ID",
                        },
                        "name": {
                            "type": "string",
                            "description": "新的聊天室名称",
                        },
                    },
                    "required": ["room_id", "name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_chat_room_detail",
                "description": "获取聊天室的详细信息（包括所有成员）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {
                            "type": "integer",
                            "description": "聊天室ID",
                        },
                    },
                    "required": ["room_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "add_users_to_chat",
                "description": "添加用户到聊天室",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {
                            "type": "integer",
                            "description": "聊天室ID",
                        },
                        "uids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "要添加的用户ID列表",
                        },
                    },
                    "required": ["room_id", "uids"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "leave_chat_room",
                "description": "离开聊天室（移除当前用户）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "room_id": {
                            "type": "integer",
                            "description": "聊天室ID",
                        },
                    },
                    "required": ["room_id"],
                },
            },
        },
        # ====================================================================
        # Upload Tools (2)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "upload_image",
                "description": "上传图片",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "图片文件的本地路径",
                        },
                    },
                    "required": ["file_path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "upload_file",
                "description": "上传任意文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "文件的本地路径",
                        },
                    },
                    "required": ["file_path"],
                },
            },
        },
        # ====================================================================
        # Utility Tools (1)
        # ====================================================================
        {
            "type": "function",
            "function": {
                "name": "get_forum_updates",
                "description": (
                    "获取论坛综合更新摘要，一次性返回未读主题和通知的汇总信息。"
                    "适用于快速了解论坛最新动态。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
    ]

    return tools


class ToolExecutor:
    """Executes tools by name, mapping to client API calls.

    Provides a clean interface for OpenAI function calling integration.
    Maps tool names to actual client methods for execution.

    Example:
        >>> executor = ToolExecutor(client)
        >>> result = executor.execute("get_notifications", {"filter": "new-mention"})
        >>> result = executor.execute("create_topic", {
        ...     "cid": 1,
        ...     "title": "Hello",
        ...     "content": "World"
        ... })
    """

    def __init__(self, client: NodeBBClient):
        """Initialize tool executor.

        Args:
            client: NodeBBClient instance
        """
        self.client = client
        self._method_map = self._build_method_map()

    def _build_method_map(self) -> Dict[str, Callable]:
        """Build mapping from tool names to client methods.

        Returns:
            Dictionary mapping tool names to callable methods
        """
        return {
            # Read API (12 tools)
            "get_notifications": self.client.read.get_notifications,
            "get_unread_count": self.client.read.get_unread_count,
            "get_unread_topics": self.client.read.get_unread_topics,
            "get_recent_posts": self.client.read.get_recent_posts,
            "get_topic": self.client.read.get_topic,
            "get_categories": self.client.read.get_categories,
            "get_category": self.client.read.get_category,
            "get_user": self.client.read.get_user,
            "get_user_by_username": self.client.read.get_user_by_username,
            "search_users": self.client.read.search_users,
            "get_config": self.client.read.get_config,
            "get_post": self.client.read.get_post,

            # Write API - Topics/Posts (12 tools)
            "create_topic": self.client.write.create_topic,
            "create_reply": self.client.write.create_reply,
            "edit_post": self.client.write.edit_post,
            "delete_post": self.client.write.delete_post,
            "delete_topic": self.client.write.delete_topic,
            "vote_post": self.client.write.vote_post,
            "unvote_post": self.client.write.unvote_post,
            "bookmark_post": self.client.write.bookmark_post,
            "unbookmark_post": self.client.write.unbookmark_post,
            "follow_topic": self.client.write.follow_topic,
            "unfollow_topic": self.client.write.unfollow_topic,
            "mark_topic_read": self.client.write.mark_topic_read,
            "mark_topic_unread": self.client.write.mark_topic_unread,

            # Write API - Topic State/Tags (6 tools)
            "set_topic_state": self.client.write.set_topic_state,
            "pin_topic": self.client.write.pin_topic,
            "unpin_topic": self.client.write.unpin_topic,
            "update_topic_tags": self.client.write.update_topic_tags,
            "add_topic_tag": self.client.write.add_topic_tag,
            "remove_topic_tags": self.client.write.remove_topic_tags,

            # Write API - Post Operations (5 tools)
            "move_post": self.client.write.move_post,
            "restore_post": self.client.write.restore_post,
            "soft_delete_post": self.client.write.soft_delete_post,
            "get_post_replies": self.client.write.get_post_replies,

            # Chat API (8 tools)
            "get_chats": self.client.chat.get_rooms,
            "create_chat_room": self.client.chat.create_room,
            "send_chat_message": self.client.chat.send_message,
            "get_chat_messages": self.client.chat.get_messages,
            "get_chat_room_detail": self.client.chat.get_room_detail,
            "add_users_to_chat": self.client.chat.add_users,
            "leave_chat_room": self.client.chat.leave_room,
            "rename_room": self.client.chat.rename_room,

            # Upload API (2 tools)
            "upload_image": self.client.upload.image,
            "upload_file": self.client.upload.post_file,

            # Utility Tools (1 tool)
            "get_forum_updates": lambda: get_forum_updates(self.client),
        }

    def execute(self, name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool by name with arguments.

        Args:
            name: Tool/function name to execute
            args: Arguments to pass to the tool

        Returns:
            Result from tool execution

        Raises:
            ValueError: If tool name is not found
            NodeBBError: If tool execution raises an error

        Example:
            >>> executor = ToolExecutor(client)
            >>> result = executor.execute("get_notifications", {"filter": "new-mention"})
            >>> result = executor.execute("create_topic", {
            ...     "cid": 1,
            ...     "title": "Hello",
            ...     "content": "World"
            ... })
        """
        if name not in self._method_map:
            available = ", ".join(self._method_map.keys())
            raise ValueError(f"Unknown tool: '{name}'. Available tools: {available}")

        method = self._method_map[name]

        try:
            return method(**args)
        except TypeError as e:
            raise ValueError(f"Invalid arguments for tool '{name}': {e}")

    def list_tools(self) -> List[str]:
        """List all available tool names.

        Returns:
            List of tool name strings
        """
        return list(self._method_map.keys())

    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get info about a specific tool.

        Args:
            name: Tool name

        Returns:
            Tool definition if found, None otherwise

        Example:
            >>> info = executor.get_tool_info("get_notifications")
        """
        tools = get_tool_definitions()
        for tool in tools:
            if tool["function"]["name"] == name:
                return tool
        return None


def execute_tool(client: NodeBBClient, name: str, args: Dict[str, Any]) -> Any:
    """Execute a tool on a client instance.

    Convenience function for single tool execution.

    Args:
        client: NodeBBClient instance
        name: Tool name to execute
        args: Tool arguments

    Returns:
        Result from tool execution

    Example:
        >>> from nodebb import NodeBBClient, NodeBBConfig
        >>> config = NodeBBConfig(base_url="https://forum.example.com", token="...")
        >>> client = NodeBBClient(config)
        >>> result = execute_tool(client, "get_notifications", {"filter": "new-mention"})
    """
    executor = ToolExecutor(client)
    return executor.execute(name, args)


# ============================================================================
# Helper functions for formatted output
# ============================================================================

def format_unread_topics_summary(result: Dict[str, Any]) -> str:
    """Format unread topics result into a human-readable summary.

    Args:
        result: Result from get_unread_topics API call

    Returns:
        Formatted string summary
    """
    lines = []
    topic_count = result.get("topicCount", 0)
    lines.append(f"未读主题总数: {topic_count}")

    topics = result.get("topics", [])
    if not topics:
        lines.append("暂无未读主题")
        return "\n".join(lines)

    lines.append(f"\n未读主题列表 ({len(topics)} 个):")
    lines.append("-" * 60)

    for i, topic in enumerate(topics, 1):
        lines.append(f"\n{i}. 【{topic.get('title', '无标题')}】")
        lines.append(f"   ID: {topic.get('tid')} | 分类: {topic.get('category', {}).get('name', '未知')}")
        lines.append(f"   作者: {topic.get('user', {}).get('username', '未知')}")
        lines.append(f"   回复: {topic.get('postcount', 0)} | 浏览: {topic.get('viewcount', 0)}")
        lines.append(f"   时间: {topic.get('timestampISO', '未知')}")

        teaser = topic.get("teaser")
        if teaser:
            content = teaser.get("content", "").strip()[:100].replace("\n", " ")
            lines.append(f"   最新回复: {content}...")

        tags = topic.get("tags", [])
        if tags:
            tag_names = [t.get("value", "") for t in tags]
            lines.append(f"   标签: {', '.join(tag_names)}")

    next_start = result.get("nextStart")
    if next_start:
        lines.append(f"\n[更多主题可用，下一页起始索引: {next_start}]")

    return "\n".join(lines)


def format_notifications_summary(result: Dict[str, Any]) -> str:
    """Format notifications result into a human-readable summary.

    Args:
        result: Result from get_notifications API call

    Returns:
        Formatted string summary
    """
    import re

    lines = []
    notifications = result.get("notifications", [])

    lines.append(f"通知总数: {len(notifications)}")

    # Count unread
    unread_count = sum(1 for n in notifications if not n.get("read", True))
    lines.append(f"未读通知: {unread_count}")

    if not notifications:
        lines.append("暂无通知")
        return "\n".join(lines)

    # Group by type
    type_counts = {}
    for n in notifications:
        t = n.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    lines.append(f"类型分布: {dict(type_counts)}")

    lines.append(f"\n通知列表 ({len(notifications)} 个):")
    lines.append("-" * 60)

    type_names = {
        "new-reply": "新回复",
        "new-topic": "新主题",
        "new-chat": "新私信",
        "new-group-chat": "群聊消息",
        "mention": "@提及",
        "follow": "新关注",
        "upvote": "点赞",
        "new-reward": "新奖励",
    }

    for i, notif in enumerate(notifications, 1):
        ntype = notif.get("type", "unknown")
        type_name = type_names.get(ntype, ntype)
        read_status = "已读" if notif.get("read") else "【未读】"

        lines.append(f"\n{i}. [{type_name}] {read_status}")

        # Clean HTML from bodyShort
        body = re.sub(r"<[^>]+>", "", notif.get("bodyShort", ""))
        lines.append(f"   {body}")

        user = notif.get("user", {})
        if user:
            lines.append(f"   来自: {user.get('username', '未知')}")

        lines.append(f"   路径: {notif.get('path', '')}")
        lines.append(f"   时间: {notif.get('datetimeISO', '未知')}")

    return "\n".join(lines)


def get_forum_updates(client: NodeBBClient) -> Dict[str, Any]:
    """Get a combined summary of forum updates (unread topics + notifications).

    This is a convenience function that combines multiple API calls into
    a single comprehensive update summary.

    Args:
        client: NodeBBClient instance

    Returns:
        Dictionary containing:
            - unread_count: Number of unread topics
            - notification_count: Number of notifications
            - unread_notification_count: Number of unread notifications
            - topics: List of unread topics (simplified)
            - notifications: List of notifications (simplified)
            - summary: Human-readable summary text
    """
    # Get unread topics
    try:
        unread_result = client.read.get_unread_topics()
        unread_count = unread_result.get("topicCount", 0)
        topics = unread_result.get("topics", [])
    except Exception:
        unread_count = 0
        topics = []

    # Get notifications
    try:
        notif_result = client.read.get_notifications()
        notifications = notif_result.get("notifications", [])
        unread_notif_count = sum(1 for n in notifications if not n.get("read", True))
    except Exception:
        notifications = []
        unread_notif_count = 0

    # Build simplified topic list
    simple_topics = []
    for t in topics[:10]:  # Limit to 10
        simple_topics.append({
            "tid": t.get("tid"),
            "title": t.get("title"),
            "author": t.get("user", {}).get("username"),
            "category": t.get("category", {}).get("name"),
            "replies": t.get("postcount"),
            "time": t.get("timestampISO"),
        })

    # Build simplified notification list
    simple_notifications = []
    for n in notifications[:10]:  # Limit to 10
        simple_notifications.append({
            "type": n.get("type"),
            "body": n.get("bodyShort", "").replace("<strong>", "").replace("</strong>", ""),
            "user": n.get("user", {}).get("username"),
            "path": n.get("path"),
            "read": n.get("read"),
            "time": n.get("datetimeISO"),
        })

    # Build summary text
    summary_parts = []
    summary_parts.append(f"论坛更新摘要:")
    summary_parts.append(f"- 未读主题: {unread_count} 个")
    summary_parts.append(f"- 通知: {len(notifications)} 个 ({unread_notif_count} 个未读)")

    if simple_topics:
        summary_parts.append("\n最近未读主题:")
        for t in simple_topics[:5]:
            summary_parts.append(f"  • [{t['tid']}] {t['title']} - {t['author']}")

    if simple_notifications:
        summary_parts.append("\n最近通知:")
        for n in simple_notifications[:5]:
            status = "🆕" if not n["read"] else "  "
            summary_parts.append(f"  {status} [{n['type']}] {n['body'][:30]}...")

    return {
        "unread_count": unread_count,
        "notification_count": len(notifications),
        "unread_notification_count": unread_notif_count,
        "topics": simple_topics,
        "notifications": simple_notifications,
        "summary": "\n".join(summary_parts),
    }
