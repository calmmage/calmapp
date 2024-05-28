import json
from typing import TYPE_CHECKING, Dict
from calmapp.plugins.plugin import Plugin
import os
from dotenv import load_dotenv
from calmlib.utils import get_logger
from collections import defaultdict

logger = get_logger(__name__)
# from loguru import logger

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class MessageHistoryPlugin(Plugin):
    name = "message_history"

    # todo: move these to app config
    save_to_memory = True
    save_to_disk = False
    # option 1: save to separate files
    # option 2: save to sqlite db / redis
    # option 3: save to csv files?
    save_to_database = False

    def __init__(self, app: "App", config: "AppConfig"):
        super().__init__(app, config)
        # in memory message history
        self.messages = []
        self.messages_by_user = defaultdict(list)
        self.messages_by_chat = defaultdict(list)
        # on disk storage - use app.app_data_path to store data
        # todo: is this fast? track time? optimize?
        if self.save_to_disk:
            # load existing messages from disk
            for file in os.listdir(self.data_path):
                # read file and load messages
                lines = open(os.path.join(self.data_path, file)).readlines()
                for line in lines:
                    message = json.loads(line.strip())
                    self.messages.append(message)
                    user_id = self.get_user_id(message)
                    self.messages_by_user[user_id].append(message)
                    chat_id = self.get_chat_id(message)
                    self.messages_by_chat[chat_id].append(message)
        self.logger.info(f"Loaded {len(self.messages)} messages from disk")

    @property
    def data_path(self):
        return os.path.join(self.app.app_data_path, "message_history")

    def get_deta_path_by_chat_id(self, chat_id):
        return os.path.join(self.data_path, f"{chat_id}.txt")

    async def save_update(self, update: Dict):
        message = self._extract_message(update)
        await self.save_message(message)

    @staticmethod
    def _extract_message(update):
        if "message" in update:
            return update["message"]
        else:
            raise ValueError("Can't find message in update")

    async def save_message(self, message: Dict):
        # todo: save per chat and per user?
        self.messages.append(message)
        if self.save_to_disk:
            # save to a csv per
            chat_id = self.get_chat_id(message)
            # todo: is this fast? track time? optimize?
            with open(self.get_deta_path_by_chat_id(chat_id), "a") as f:
                f.write(json.dumps(message) + "\n")

    @staticmethod
    def get_chat_id(message):
        # todo: handle stupid-dupid cases:
        #  a) what if messages is forwarded - get original or new?
        #  b) that 'supergroup' thing where -100 is added to chat_id
        #  c) telegram - has it in ['chat']['id']
        if "chat_id" in message:
            return message["chat_id"]
        elif "chat" in message and "id" in message["chat"]:
            return message["chat"]["id"]
        else:
            raise ValueError("Chat id not found in message")

    @staticmethod
    def get_user_id(message):
        # todo: handle stupid cases:
        #  a) use username instead of user_id - when?
        #  b) telegarm - has it in ['from']['id']
        #  c) what if message is forwarded - get original or new?
        if "user_id" in message:
            return message["user_id"]
        elif "from" in message and "id" in message["from"]:
            return message["from"]["id"]
        else:
            raise ValueError("User id not found in message")

    def get_messages_by_user(self, user_id):
        return [m for m in self.messages if self.get_user_id(m) == user_id]

    def get_messages_by_chat_id(self, chat_id):
        return [m for m in self.messages if self.get_chat_id(m) == chat_id]
