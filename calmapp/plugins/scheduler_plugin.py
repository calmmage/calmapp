from typing import TYPE_CHECKING

from calmapp.plugins.plugin import Plugin
import os
from dotenv import load_dotenv
from calmlib.utils import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class SchedulerPlugin(Plugin):
    name = "scheduler"

    def __init__(self, app: App, config: AppConfig):
        super().__init__(app, config)

        # use apscheduler
        # from apscheduler.schedulers.background import BackgroundScheduler
        # scheduler = BackgroundScheduler()
        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        # todo: rename shorter - e.g. core - for easy access
        self._scheduler = AsyncIOScheduler()

    @property
    def core(self):
        return self._scheduler
