from typing import TYPE_CHECKING

from calmapp.plugins.plugin import Plugin
import os
from dotenv import load_dotenv
from calmlib.utils import get_logger
from .gpt_plugin import GptPlugin

logger = get_logger(__name__)
# from loguru import logger

if TYPE_CHECKING:
    from calmapp.app import App
    from calmapp.app_config import AppConfig


class OpenAIPlugin(GptPlugin):
    name = "openai"

    def __init__(self, app: "App", config: "AppConfig"):
        super().__init__(app, config)
        api_key = config.openai_api_key.get_secret_value()

        # todo: use plugin config instead
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key is required for GPT plugin. "
                "Please provide it as an argument "
                "or in the environment variable OPENAI_API_KEY."
            )
        from openai import AsyncOpenAI

        self._gpt = AsyncOpenAI(api_key=api_key)
        # self._gpt.api_key = api_key

    @staticmethod
    def _build_warmup_messages(warmup_messages):
        sample_message = warmup_messages[0]
        # validate that it's a tuple with 2 elements
        if isinstance(sample_message, tuple) and len(sample_message) == 2:
            result = []
            for message in warmup_messages:
                result.extend(
                    [
                        {"role": "user", "content": message[0]},
                        {"role": "assistant", "content": message[1]},
                    ]
                )
            return result
        elif (
            isinstance(sample_message, dict)
            and sample_message.get("role")
            and sample_message.get("content")
        ):
            return warmup_messages
        else:
            raise ValueError(
                "warmup_messages should be a list of tuples "
                "or a list of dicts with 'role' and 'content' keys"
            )

    async def complete_text(
        self,
        text: str,
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 100,
        warmup_messages=None,
        temperature: float = 0.5,
        system="You are a helpful assistant.",
        **kwargs,
    ):
        # todo: sanity check token counts for the limits
        messages = [
            {"role": "system", "content": system},
        ]
        if warmup_messages:
            messages += self._build_warmup_messages(warmup_messages)
        messages.append({"role": "user", "content": text})
        response = await self._gpt.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )
        finish_reason = response.choices[0].finish_reason
        if finish_reason != "stop":
            logger.warning(
                f"Completion stopped due to the following reason: {finish_reason}"
            )
        return response.choices[0].message.content
