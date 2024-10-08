from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic import SecretStr
from pydantic_settings import BaseSettings

from calmapp.plugins.database_plugin_config import DatabaseConfig

load_dotenv()

DEFAULT_APP_DATA_PATH = "app_data"


class PluginFlags(BaseSettings):
    enable_gpt_engine: bool = False
    enable_langchain: bool = False
    enable_light_llm: bool = False
    enable_openai: bool = False
    enable_database: bool = False
    enable_logging: bool = False
    enable_message_history: bool = False
    enable_scheduler: bool = False
    enable_whisper: bool = False

    class Config:
        extra = "ignore"


class AppConfig(BaseSettings):
    app_data_path: Path = DEFAULT_APP_DATA_PATH

    database: DatabaseConfig = DatabaseConfig()
    # telegram_bot: TelegramBotConfig = TelegramBotConfig()
    # todo: deprecate and use openai plugin instead
    enable_openai_api: bool = False
    openai_api_key: SecretStr = SecretStr("")

    # Plugin enable flags
    plugin_flags: PluginFlags = PluginFlags()
    plugins: List[str] = []

    # Other settings
    # todo: deprecate and use whisper plugin instead
    enable_voice_recognition: bool = False
    process_audio_in_parallel: bool = False

    # todo: add extra {APP}_ prefix to all env vars?
    #  will this work?
    #  "env_prefix": "{APP}_TELEGRAM_BOT_",

    model_config = ConfigDict(extra="ignore")
