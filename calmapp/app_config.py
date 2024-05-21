from pathlib import Path

# from typing import Optional

# from aiogram.enums import ParseMode
from dotenv import load_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings

load_dotenv()


class DatabaseConfig(BaseSettings):
    conn_str: SecretStr = SecretStr("")
    name: str = ""

    model_config = {
        "env_prefix": "DATABASE_",
    }


DEFAULT_APP_DATA_PATH = "app_data"


class AppConfig(BaseSettings):
    app_data_path: Path = DEFAULT_APP_DATA_PATH

    database: DatabaseConfig = DatabaseConfig()
    # telegram_bot: TelegramBotConfig = TelegramBotConfig()
    # todo: deprecate and use openai plugin instead
    enable_openai_api: bool = False
    openai_api_key: SecretStr = SecretStr("")

    # Plugin enable flags
    enable_gpt_engine_plugin: bool = False
    enable_langchain_plugin: bool = False
    enable_light_llm_plugin: bool = False
    enable_openai_plugin: bool = False
    enable_database_plugin: bool = False
    enable_logging_plugin: bool = False
    enable_message_history_plugin: bool = False
    enable_scheduler_plugin: bool = False
    enable_whisper_plugin: bool = False

    # Other settings
    # todo: deprecate and use whisper plugin instead
    enable_voice_recognition: bool = False
    process_audio_in_parallel: bool = False
    # todo: deprecate and use scheduler plugin instead
    enable_scheduler: bool = False

    # todo: add extra {APP}_ prefix to all env vars?
    #  will this work?
    #  "env_prefix": "{APP}_TELEGRAM_BOT_",
