from typing import TYPE_CHECKING, Dict
from calmapp.plugins.plugin import Plugin
import os
from dotenv import load_dotenv
from calmlib.utils import get_logger

logger = get_logger(__name__)
# from loguru import logger

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class MessageHistoryPlugin(Plugin):
    name = "message_history"

    def __init__(self, app: App, config: AppConfig):
        super().__init__(app, config)
        # in memory message history
        self.messages = []

    def save_message(self, message: Dict):
        self.messages.append(message)

    def get_messages_by_user(self, user_id):
        return [m for m in self.messages if m["user_id"] == user_id]

    def get_messages_by_chat_id(self, chat_id):
        return [m for m in self.messages if m["chat_id"] == chat_id]
