from calmapp import App

from enum import Enum
import json

from abstract_tool_user.utils import query_prompt


class ConversationMode(Enum):
    SIMPLE = 1  # dumb and simple - send the user message as is
    WITH_HISTORY = 2  # send user message with chat history
    SWITCH = 3  # control chat history - switch conversations
    DROP = 4  # drop / shorten messages if history is too long
    LARGE_CONTEXT = 5  # use a model with larger context window


class MyApp(App):
    # region 1 - single user single topic conversations
    @property
    def single_user_messages_path(self):
        return self.app_data_path / "single_user_messages.json"

    @property
    def single_user_archive_path(self):
        return self.app_data_path / "single_user_archive.json"

    def _single_user_save_message(self, input_str, output_str):
        self.messages.append(input_str)
        self.messages.append(output_str)
        import json

        json.dump(self.messages, open(self.single_user_messages_path, "w"))

    async def _single_user_save_archive(self):
        json.dump(self.messages, open(self.single_user_messages_path, "w"))
        json.dump(self.archive, open(self.single_user_archive_path, "w"))

    def _single_user_load_messages(self):
        if self.single_user_messages_path.exists():
            self.messages = json.load(open(self.single_user_messages_path))
        if self.single_user_archive_path.exists():
            self.archive = json.load(open(self.single_user_archive_path))
        # move old messages to archive
        if self.messages:
            self.reset()

    # endregion 1 - single user single topic conversations

    def save_message(self, input_str, output_str):
        if self.conversation_mode == ConversationMode.WITH_HISTORY:
            self._single_user_save_message(input_str, output_str)
        else:
            raise NotImplementedError(
                f"Saving messages is not implemented for this conversation mode {self.conversation_mode}"
            )

    def load_messages(self):
        if self.conversation_mode == ConversationMode.WITH_HISTORY:
            self._single_user_load_messages()
        else:
            raise NotImplementedError(
                f"Loading messages is not implemented for this conversation mode {self.conversation_mode}"
            )

    def __init__(
        self, conversation_mode: ConversationMode = ConversationMode.SIMPLE, **kwargs
    ):
        """Initialize the gpt agent and the toolkit"""
        super().__init__(**kwargs)
        self.conversation_mode = conversation_mode

        self.messages = []
        self.archive = []
        self.load_messages()

    def invoke(self, input_str: str) -> str:
        """Invoke the gpt agent with the input string and return the response."""

        # version 0: dumb and simple - send the user message as is
        if self.conversation_mode == ConversationMode.SIMPLE:
            return query_prompt(input_str)

        # version 1: send user message with chat history
        if self.conversation_mode == ConversationMode.WITH_HISTORY:
            self.messages.append(input_str)
            # todo: add retries?
            try:
                output_str = query_prompt(
                    prompt=input_str,
                    warmup_messages=self.messages,
                )
            except Exception as e:
                output_str = f"Failed to generate a response, error: {e}"
            self.messages.append(output_str)
            return output_str

        # version 2: control chat history - switch conversations

        # version 3: drop / shorten messages if history is too long
        # or use a model with larger context window

        # version 4:

        # version 5:

    async def reset(self):
        if self.conversation_mode == ConversationMode.WITH_HISTORY:
            self.archive.append(self.messages)
            self.messages = []
            await self._single_user_save_archive()
        else:
            # todo: capture errors with aiogram and notify user the bot crashed.
            raise NotImplementedError(
                f"Resetting the chat history is not implemented for this conversation mode {self.conversation_mode}"
            )
