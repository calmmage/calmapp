from typing import TYPE_CHECKING

from calmapp.plugins.plugin import Plugin

if TYPE_CHECKING:
    from calmapp.app import App


class SchedulerPlugin(Plugin):
    name = "scheduler"

    def __init__(self, app: "App", **kwargs):
        super().__init__(app, **kwargs)

        from apscheduler.schedulers.asyncio import AsyncIOScheduler

        self._scheduler = AsyncIOScheduler()

    @property
    def core(self):
        return self._scheduler
