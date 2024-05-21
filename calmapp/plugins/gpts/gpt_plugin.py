from typing import TYPE_CHECKING, List, Dict

from calmapp.plugins.plugin import Plugin
from calmlib.utils import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class GptPlugin(Plugin):
    def __init__(self, app: App, config: AppConfig):
        super().__init__(app, config)

    def complete(self, model: str, messages: List[str], **kwargs: Dict) -> str:
        raise NotImplementedError

    async def acomplete(self, model: str, messages: List[str], **kwargs: Dict) -> str:
        raise NotImplementedError

    def embeddings(self, text: str, **kwargs: Dict) -> Any:
        raise NotImplementedError

    def chat(self, messages: List[str], **kwargs: Dict) -> str:
        raise NotImplementedError

    def voice_recognition(self, audio_data: bytes, **kwargs: Dict) -> str:
        raise NotImplementedError
