from enum import Enum
from loguru import logger
from pydantic import BaseModel
from typing import List

from .config import AppConfig
from .notion_handler import NotionHandler


class AppResponseStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class AppResponse(BaseModel):
    status: AppResponseStatus
    message: str = None


class App:
    def __init__(self, **kwargs) -> None:
        logger.info("Initializing App")
        self.config = AppConfig(**kwargs)
        self.notion_handler = NotionHandler(self.config.notion_token,
                                            self.config.notion_db_id)
        logger.info("App initialized")

    @property
    def db_url(self) -> str:
        logger.info("Retrieving database URL")
        return self.notion_handler.get_url()

    def process_message(self, message_text: str) -> str:
        logger.info(f"Processing message: {message_text}")
        self.notion_handler.save_message(message_text)
        logger.info("Message saved")
        return "Message saved"

    async def process_message_async(
            self, message_text: str, content=None
    ) -> AppResponse:
        try:
            logger.info(f"Processing message asynchronously: {message_text}")
            await self.notion_handler.save_message(message_text)
            logger.info("Message saved asynchronously")
            # todo: provide message (notion) url in response?
            # todo: forward messages to sanctuary somewhere? And links there
            return AppResponse(status=AppResponseStatus.SUCCESS)
        except Exception as e:
            # todo: report errors to the user?
            logger.exception(e)
            return AppResponse(status=AppResponseStatus.FAILURE,
                               message=str(e))

    async def get_messages_async(self, limit=None) -> List[str]:
        logger.info("Retrieving messages asynchronously")
        messages = await self.notion_handler.get_messages_async(limit=limit)
        logger.info(f"{len(messages)} messages retrieved asynchronously")
        return messages


if __name__ == '__main__':
    import sys
    from config import LoggingConfig

    logging_config = LoggingConfig()
    # set logging level
    logger.remove()
    # set up console logger
    logger.add(sys.stdout,
               level=logging_config.level,
               rotation="1 week",
               serialize=False)
    # file logger
    if logging_config.filepath:
        logger.add(logging_config.filepath,
                   level=logging_config.level,
                   rotation="1 week",
                   serialize=False)
    logger.info("Logging configured")
