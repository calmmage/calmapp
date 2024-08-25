import abc
from typing import TYPE_CHECKING, Type
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    from calmapp.app import App


class PluginConfig(BaseSettings):
    class Config:
        extra = "ignore"


class Plugin(abc.ABC):
    name: str = None
    config_class: Type[PluginConfig] = PluginConfig

    def __init__(self, app: "App", **kwargs):  #  old config: , config: "AppConfig"
        self.config = self.config_class(**kwargs)
        self.app = app
        # # bind logger
        self.logger = self.app.logger.bind(plugin=self.name)
        self.logger.info(f"Initializing {self.name} plugin")
