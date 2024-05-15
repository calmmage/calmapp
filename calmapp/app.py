from collections import defaultdict
from pathlib import Path

import asyncio
from typing import Type, Union

import loguru
import mongoengine
import openai
from dotenv import load_dotenv

# from apscheduler.triggers.interval import IntervalTrigger
# from bot_lib.migration_bot_base.core import DatabaseConfig  # , TelegramBotConfig
from calmapp.app_config import AppConfig, DatabaseConfig

# from bot_lib.migration_bot_base.core.telegram_bot import TelegramBot
from calmlib.beta.utils import (
    DEFAULT_PERIOD,
    DEFAULT_BUFFER,
    split_and_transcribe_audio,
    Audio,
)

from calmapp.plugins import Plugin, GptPlugin

# from bot_lib.plugins import GptPlugin
from typing import List, Type

# from bot_lib.migration_bot_base.core.app import App as OldApp


Pathlike = Union[str, Path]


class App:
    """"""

    # region old AppBase

    _app_config_class: Type[AppConfig] = AppConfig
    # _telegram_bot_class: Type[TelegramBot] = TelegramBot
    _database_config_class: Type[DatabaseConfig] = DatabaseConfig
    # _telegram_bot_config_class: Type[TelegramBotConfig] = TelegramBotConfig

    def _init_app_base(self, data_dir=None, config: _app_config_class = None):
        self.logger = loguru.logger.bind(component=self.__class__.__name__)
        if config is None:
            config = self._load_config()
        if data_dir is not None:
            config.data_dir = Path(data_dir)
        self.config = config
        self.db = self._connect_db()
        # self.bot = self._telegram_bot_class(config.telegram_bot, app=self)
        self.logger.info(f"Loaded config: {self.config}")

    @property
    def data_dir(self):
        if not self.config.data_dir.exists():
            self.config.data_dir.mkdir(parents=True, exist_ok=True)
        return self.config.data_dir

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

    name: str = None
    start_message = "Hello! I am {name}. {description}"
    help_message = "Help! I need somebody! Help! Not just anybody! Help! You know I need someone! Help!"

    def __init__(
        self,
        plugins: List[Type[Plugin]] = None,
        data_dir: Pathlike = None,
        config: _app_config_class = None,
    ):
        # super().__init__()
        self._init_app_base(data_dir, config)
        self._init_old_app(config)
        if plugins is None:
            plugins = []
        self.plugins = {plugin.name: plugin() for plugin in plugins}

    @property
    def gpt(self) -> GptPlugin:
        if "gpt" not in self.plugins:
            raise AttributeError("GPT plugin is not enabled.")
        return self.plugins["gpt"]

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

    hidden_commands = defaultdict(list)

    # endregion

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
