from .plugin import Plugin
from .gpts.gpt_plugin import GptPlugin
from .gpts.openai_plugin import OpenAIPlugin
from .gpts.langchain_plugin import LangChainPlugin
from .gpts.gpt_engine_plugin import GptEnginePlugin
from .gpts.light_llm_plugin import LightLLMPlugin
from .database_plugin import DatabasePlugin
from .logging_plugin import LoggingPlugin
from .message_history_plugin import MessageHistoryPlugin
from .scheduler_plugin import SchedulerPlugin
from .whisper_plugin import WhisperPlugin

available_plugins = {
    "gpt_engine": GptEnginePlugin,
    "langchain": LangChainPlugin,
    "light_llm": LightLLMPlugin,
    "openai": OpenAIPlugin,
    "database": DatabasePlugin,
    "logging": LoggingPlugin,
    "message_history": MessageHistoryPlugin,
    "scheduler": SchedulerPlugin,
    "whisper": WhisperPlugin,
}
