import asyncio
from collections import defaultdict
from pathlib import Path
from typing import List, Type, TYPE_CHECKING, Union

import loguru
import typing_extensions
from calmlib.utils.audio_utils import DEFAULT_PERIOD, DEFAULT_BUFFER, split_and_transcribe_audio, Audio
from dotenv import load_dotenv

# from apscheduler.triggers.interval import IntervalTrigger
from calmapp.app_config import AppConfig, DatabaseConfig

# from bot_lib.migration_bot_base.core.app import App as OldApp
if TYPE_CHECKING:
    from calmapp.plugins import (
        Plugin,
        MessageHistoryPlugin,
        WhisperPlugin,
        SchedulerPlugin,
        OpenAIPlugin,
        DatabasePlugin,
        LangChainPlugin,
        GptPlugin,
        LightLLMPlugin,
        LoggingPlugin,
    )

Pathlike = Union[str, Path]


class AppBase:
    """"""

    # region old AppBase

    _app_config_class: Type[AppConfig] = AppConfig
    # _telegram_bot_class: Type[TelegramBot] = TelegramBot
    _database_config_class: Type[DatabaseConfig] = DatabaseConfig

    # _telegram_bot_config_class: Type[TelegramBotConfig] = TelegramBotConfig

    def _init_app_base(self, app_data_path=None, config: _app_config_class = None, **kwargs):
        self.logger = loguru.logger.bind(component=self.__class__.__name__)
        if config is None:
            config = self._load_config(**kwargs)
        if app_data_path is not None:
            config.app_data_path = Path(app_data_path)
        self.config = config
        # todo: instead of initializing db here, initialize it in the database plugin
        # self.bot = self._telegram_bot_class(config.telegram_bot, app=self)
        self.logger.info(f"Loaded config: {self.config}")

    @property
    def db(self):
        return self.database.db

    @property
    def app_data_path(self):
        self.config.app_data_path.mkdir(parents=True, exist_ok=True)
        return self.config.app_data_path

    @property
    @typing_extensions.deprecated(
        "The `data_dir` property is deprecated; use `app_data_path` instead.",
    )
    def data_dir(self):
        return self.app_data_path

    # todo_optional: setter, moving the data to the new dir

    # todo: move to plugins - enable or disable app config?
    def _load_config(self, **kwargs):
        load_dotenv()
        database_config = self._database_config_class(**kwargs)
        # telegram_bot_config = self._telegram_bot_config_class(**kwargs)
        return self._app_config_class(
            database=database_config,
            # telegram_bot=telegram_bot_config,
            **kwargs,
        )

    # endregion

    # region old App

    # ------------------ GPT Engine ------------------ #

    # ------------------ Audio ------------------ #
    # region Audio

    # todo: move to plugins - whisper
    async def parse_audio(
        self,
        audio: Audio,
        period: int = DEFAULT_PERIOD,
        buffer: int = DEFAULT_BUFFER,
        parallel: bool = None,
    ):
        if parallel is None:
            parallel = self.config.process_audio_in_parallel
        chunks = await split_and_transcribe_audio(
            audio,
            period=period,
            buffer=buffer,
            parallel=parallel,
            logger=self.logger,
        )
        return chunks

    # endregion
    # --------------------------------------------- #

    async def _run_with_scheduler(self, dp=None, bot=None):
        # this seems stupid, but this is a tested working way, so i go with it
        # rework sometime later - probably can just start and not gather
        self.scheduler.core.start()
        if bot is not None:
            await dp.start_polling(bot)

    def run(self, dp=None, bot=None):
        if self.config.enable_scheduler:
            self.logger.info("Running with scheduler")
            asyncio.run(self._run_with_scheduler(dp, bot))
        else:
            self.logger.info(f"Starting {self.__class__.__name__}")
            if bot is None:
                raise NotImplementedError("Can't run the app without a bot currently.")
            asyncio.run(dp.start_polling(bot))

    # endregion

    # region bot-lib app base

    plugins_required: List[str] = []

    def __init__(
        self,
        plugins: List[Type["Plugin"]] = None,
        app_data_path: Pathlike = None,
        config: _app_config_class = None,
        **kwargs,
    ):
        self.plugins = {}
        self._init_app_base(app_data_path, config, **kwargs)
        self._init_plugins(plugins, **kwargs)

        # check if all required plugins are present
        for plugin in self.plugins_required:
            if plugin not in self.plugins:
                raise AttributeError(f"{plugin} plugin is required.")

    # region Plugins

    def _init_plugins(self, plugins: List[Union[Type["Plugin"], str]] = None, **kwargs):
        # Step 1: Initialize plugins from arguments
        from calmapp.plugins import available_plugins

        if plugins is None:
            plugins = []

        plugin_names = set()

        # Step 1: add plugins from arguments
        for plugin in plugins:
            if isinstance(plugin, str):
                plugin_names.add(plugin)
            else:
                available_plugins[plugin.name] = plugin
                plugin_names.add(plugin.name)

        # Step 2: add plugins from config list
        for plugin in self.config.plugins:
            plugin_names.add(plugin)

        # Step 3: Add plugins enabled in the config by flags
        enabled = self.config.plugin_flags.model_dump()
        for plugin in enabled:
            if enabled[plugin]:
                plugin_names.add(plugin)

        for plugin in plugin_names:
            plugin_class = available_plugins[plugin]
            self.plugins[plugin] = plugin_class(app=self, **kwargs)

    def get_plugin(self, plugin_key: str) -> "Plugin":
        if plugin_key not in self.plugins:
            from calmapp.plugins import available_plugins

            plugin_name = available_plugins[plugin_key].name
            raise AttributeError(f"{plugin_name} plugin is not enabled.")
        return self.plugins[plugin_key]

    @property
    def scheduler(self) -> "SchedulerPlugin":
        return self.get_plugin("scheduler")

    @property
    def langchain(self) -> "LangChainPlugin":
        return self.get_plugin("langchain")

    @property
    def light_llm(self) -> "LightLLMPlugin":
        return self.get_plugin("light_llm")

    @property
    def openai(self) -> "OpenAIPlugin":
        return self.get_plugin("openai")

    @property
    def database(self) -> "DatabasePlugin":
        return self.get_plugin("database")

    @property
    def logging(self) -> "LoggingPlugin":
        return self.get_plugin("logging")

    @property
    def message_history(self) -> "MessageHistoryPlugin":
        return self.get_plugin("message_history")

    @property
    def whisper(self) -> "WhisperPlugin":
        return self.get_plugin("whisper")

    @property
    def gpt(self) -> "GptPlugin":
        """Get the first available GPT plugin."""
        gpt_plugins = {"openai", "light_llm", "langchain", "gpt_engine"}
        for plugin in gpt_plugins:
            try:
                return self.get_plugin(plugin)
            except AttributeError:
                pass
        raise AttributeError("None of the GPT plugins are enabled.")

    def __getattr__(self, name):
        # Check if the attribute exists in the AppBase instance
        if name in self.__dict__:
            return self.__dict__[name]

        # Check if the attribute exists in any of the plugins
        for plugin in self.plugins.values():
            if hasattr(plugin, name):
                return getattr(plugin, name)

        # If the attribute is not found, raise an AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object and its plugins have no attribute '{name}'")

    # endregion Plugins

    # region base commands

    name: str = None
    start_message = "Hello! I am {name}. {description}"
    help_message = "Help! I need somebody! Help! Not just anybody! Help! You know I need someone! Help!"

    @property
    def description(self):
        return self.__doc__

    def get_start_message(self):
        return self.start_message.format(name=self.name, description=self.description)

    def get_help_message(self):
        help_message = self.help_message
        if self.hidden_commands:
            help_message += "\n\nHidden commands:\n"
            for handler, commands in self.hidden_commands.items():

                help_message += f"\n{handler}:\n"
                for command in commands:
                    help_message += f"/{command}\n"

        return help_message

    # endregion

    hidden_commands = defaultdict(list)

    # region Invoke and run templates
    # enable dummy UI though single entry point
    def invoke(self, input_str: str) -> str:
        output_str = input_str
        return output_str

    def naive_run(self):
        print(f"Running app {self.name}")
        print("To exit type 'exit'")
        while True:
            input_str = input("User: ")
            if input_str == "exit":
                break
            print("App:", self.invoke(input_str))

    # endregion


App = AppBase

if __name__ == "__main__":
    app = App()

    app.naive_run()
