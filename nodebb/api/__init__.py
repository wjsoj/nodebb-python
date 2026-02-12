"""
API modules for NodeBB client.

Organizes API endpoints into logical modules.
"""

from nodebb.api.read import ReadAPI
from nodebb.api.write import WriteAPI
from nodebb.api.chat import ChatAPI
from nodebb.api.upload import UploadAPI
from nodebb.api.auth import AuthAPI

__all__ = [
    "ReadAPI",
    "WriteAPI",
    "ChatAPI",
    "UploadAPI",
    "AuthAPI",
]
