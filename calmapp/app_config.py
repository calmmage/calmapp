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


DEFAULT_DATA_DIR = "app_data"


class AppConfig(BaseSettings):
    data_dir: Path = DEFAULT_DATA_DIR

    database: DatabaseConfig = DatabaseConfig()
    # telegram_bot: TelegramBotConfig = TelegramBotConfig()
    # todo: use this setting. Deprecated
    enable_openai_api: bool = False
    enable_gpt_engine: bool = False
    openai_api_key: SecretStr = SecretStr("")

    # todo: use this setting
    enable_voice_recognition: bool = False
    process_audio_in_parallel: bool = False

    # todo: use this setting
    enable_scheduler: bool = False

    # todo: add extra {APP}_ prefix to all env vars?
    #  will this work?
    #  "env_prefix": "{APP}_TELEGRAM_BOT_",
