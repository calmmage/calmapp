from typing import TYPE_CHECKING
import shutil
from calmapp.plugins.plugin import Plugin

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class WhisperPlugin(Plugin):
    name = "whisper"

    def __init__(self, app: "App", config: "AppConfig"):
        super().__init__(app, config)

        # todo: check that codecs are installed
        #  install if necessary
        # todo: check that ffmpeg is installed
        if not self._check_ffmpeg_available():
            raise ValueError("Ffmpeg is required for whisper plugin")
        # todo: check pyrogram token and api_id

    @staticmethod
    def _check_ffmpeg_available():
        return shutil.which("ffmpeg") is not None
