from bot_lib import App, Handler, HandlerDisplayMode
from aiogram.types import Message
from collections import defaultdict
import asyncio
from calmlib.utils import get_logger

logger = get_logger(__name__)


class MyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.user_message_queue = defaultdict(asyncio.Queue)
        self.user_lock = defaultdict(asyncio.Lock)

