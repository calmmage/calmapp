import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class Plugin(abc.ABC):
    name: str = None

    def __init__(self, app: "App", config: "AppConfig"):
        self.app = app
        self.config = config
        # bind logger
        self.logger = self.app.logger.bind(plugin=self.name)
        self.logger.info(f"Initializing {self.name} plugin")
