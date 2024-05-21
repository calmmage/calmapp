import asyncio
from collections import defaultdict
from pathlib import Path

# from bot_lib.plugins import GptPlugin
from typing import List, Type
from typing import Union

import loguru
import mongoengine
import openai
import typing_extensions

# from bot_lib.migration_bot_base.core.telegram_bot import TelegramBot
from calmlib.beta.utils import (
    DEFAULT_PERIOD,
    DEFAULT_BUFFER,
    split_and_transcribe_audio,
    Audio,
)
from dotenv import load_dotenv

# from apscheduler.triggers.interval import IntervalTrigger
# from bot_lib.migration_bot_base.core import DatabaseConfig  # , TelegramBotConfig
from calmapp.app_config import AppConfig, DatabaseConfig
from calmapp.plugins import Plugin, available_plugins

# from bot_lib.migration_bot_base.core.app import App as OldApp


Pathlike = Union[str, Path]


class App:
    """"""

    # region old AppBase

    _app_config_class: Type[AppConfig] = AppConfig
    # _telegram_bot_class: Type[TelegramBot] = TelegramBot
    _database_config_class: Type[DatabaseConfig] = DatabaseConfig

    # _telegram_bot_config_class: Type[TelegramBotConfig] = TelegramBotConfig

    def _init_app_base(self, app_data_path=None, config: _app_config_class = None):
        self.logger = loguru.logger.bind(component=self.__class__.__name__)
        if config is None:
            config = self._load_config()
        if app_data_path is not None:
            config.app_data_path = Path(app_data_path)
        # make dir
        self.config = config
        self.db = self._connect_db()
        # self.bot = self._telegram_bot_class(config.telegram_bot, app=self)
        self.logger.info(f"Loaded config: {self.config}")

    @property
    def app_data_path(self):
        self.config.app_data_path.mkdir(parents=True, exist_ok=True)
        return self.config.app_data_path

    @typing_extensions.deprecated(
        "The `data_dir` property is deprecated; use `app_data_path` instead.",
        category=DeprecationWarning,
    )
    @property
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

    # todo: move to plugins
    def _connect_db(self):
        try:
            return mongoengine.get_connection("default")
        except mongoengine.connection.ConnectionFailure:
            db_config = self.config.database
            conn_str = db_config.conn_str.get_secret_value()
            return mongoengine.connect(
                db=db_config.name,
                host=conn_str,
            )

    # endregion

    # region old App

    def _init_old_app(self, config: AppConfig = None):
        # super().__init__(data_dir=data_dir, config=config)
        if self.config.enable_openai_api:
            # deprecate this
            self.logger.warning("OpenAI API is deprecated, use GPT Engine instead")
            self._init_openai()

        if self.config.enable_voice_recognition:
            self.logger.info("Initializing voice recognition")
            self._init_voice_recognition()

        # todo: move to plugins - scheduler
        self._scheduler = None
        if self.config.enable_scheduler:
            self.logger.info("Initializing scheduler")
            from apscheduler.schedulers.asyncio import AsyncIOScheduler

            # self._init_scheduler()
            self._scheduler = AsyncIOScheduler()

        # todo: move to plugins - gpt engine
        self.gpt_engine = None
        if self.config.enable_gpt_engine:
            self.logger.info("Initializing GPT Engine")
            from gpt_kit.gpt_engine.gpt_engine import GptEngine

            self.gpt_engine = GptEngine(config.gpt_engine, app=self)
            # self._init_gpt_engine()

    def _init_openai(self):
        openai.api_key = self.config.openai_api_key.get_secret_value()

    # def _init_scheduler(self):
    #     self._scheduler = AsyncIOScheduler()

    # ------------------ GPT Engine ------------------ #

    # ------------------ Audio ------------------ #

    def _init_voice_recognition(self):
        # todo: check that codecs are installed
        #  install if necessary
        # todo: check that ffmpeg is installed
        # todo: check pyrogram token and api_id
        pass

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

    # --------------------------------------------- #

    async def _run_with_scheduler(self):
        # this seems stupid, but this is a tested working way, so i go with it
        # rework sometime later - probably can just start and not gather
        self._scheduler.start()
        # await self.bot.run()
        raise NotImplementedError

    def run(self):
        if self.config.enable_scheduler:
            self.logger.info("Running with scheduler")
            asyncio.run(self._run_with_scheduler())
        else:
            # super().run()
            self.logger.info(f"Starting {self.__class__.__name__}")
            # asyncio.run(self.bot.run())
            raise NotImplementedError

    # endregion

    # region bot-lib app base

    def __init__(
        self,
        plugins: List[Type[Plugin]] = None,
        app_data_path: Pathlike = None,
        config: _app_config_class = None,
    ):
        self._init_app_base(app_data_path, config)
        self._init_old_app(config)
        self._init_plugins(plugins)

    def _init_plugins(self, plugins: List[Type[Plugin]]):
        # Initialize plugins from arguments
        if plugins is None:
            plugins = []
        self.plugins = {
            plugin.name: plugin(app=self, config=self.config) for plugin in plugins
        }

        # Initialize plugins from flags
        plugin_flags = {
            "gpt_engine": self.config.enable_gpt_engine_plugin,
            "langchain": self.config.enable_langchain_plugin,
            "light_llm": self.config.enable_light_llm_plugin,
            "openai": self.config.enable_openai_plugin,
            "database": self.config.enable_database_plugin,
            "logging": self.config.enable_logging_plugin,
            "message_history": self.config.enable_message_history_plugin,
            "scheduler": self.config.enable_scheduler_plugin,
            "whisper": self.config.enable_whisper_plugin,
        }
        for plugin_key, enabled in plugin_flags.items():
            if enabled and plugin_key not in self.plugins:
                plugin_class = available_plugins[plugin_key]
                self.plugins[plugin_key] = plugin_class(app=self, config=self.config)

    # region plugin properties
    def get_plugin(self, plugin_name: str):
        if plugin_name not in self.plugins:
            raise AttributeError(f"{plugin_name.capitalize()} plugin is not enabled.")
        return self.plugins[plugin_name]

    @property
    def scheduler(self):
        return self.get_plugin("scheduler")

    @property
    def langchain(self):
        return self.get_plugin("langchain")

    @property
    def light_llm(self):
        return self.get_plugin("light_llm")

    @property
    def openai(self):
        return self.get_plugin("openai")

    @property
    def database(self):
        return self.get_plugin("database")

    @property
    def logging(self):
        return self.get_plugin("logging")

    @property
    def message_history(self):
        return self.get_plugin("message_history")

    @property
    def whisper(self):
        return self.get_plugin("whisper")

    @property
    def gpt(self):
        """Get the first available GPT plugin."""
        gpt_plugins = {"openai", "light_llm", "langchain", "gpt_engine"}
        for plugin in gpt_plugins:
            try:
                return self.get_plugin(plugin)
            except AttributeError:
                pass
        raise AttributeError("None of the GPT plugins are enabled.")

    # endregion

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


if __name__ == "__main__":
    app = App()

    app.naive_run()
