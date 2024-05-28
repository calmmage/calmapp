from typing import TYPE_CHECKING

from calmapp.plugins.plugin import Plugin
import os
from dotenv import load_dotenv
from calmlib.utils import get_logger

from .gpt_plugin import GptPlugin

logger = get_logger(__name__)
# from loguru import logger

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class LightLLMPlugin(GptPlugin):
    name = "light_llm"

    def __init__(self, app: "App", config: "AppConfig"):
        super().__init__(app, config)
