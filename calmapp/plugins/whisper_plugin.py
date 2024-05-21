from typing import TYPE_CHECKING

from calmapp.plugins.plugin import Plugin
from calmlib.utils import get_logger

logger = get_logger(__name__)
# from loguru import logger

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class WhisperPlugin(Plugin):
    name = "whisper"

    def __init__(self, app: App, config: AppConfig):
        super().__init__(app, config)
