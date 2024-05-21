from typing import TYPE_CHECKING

from dotenv import load_dotenv
from .gpt_plugin import GptPlugin

load_dotenv()

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class GptEnginePlugin(GptPlugin):
    name = "gpt_engine"

    def __init__(self, app: "App", config: "AppConfig"):
        super().__init__(app, config)

        from gpt_kit.gpt_engine.gpt_engine import GptEngine

        # todo: sort out this mess, init the gpt engine config properly.. ?
        self._gpt_engine = GptEngine(app=self)
