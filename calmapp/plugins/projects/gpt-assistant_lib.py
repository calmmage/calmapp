from aiogram.types import Message

# import asyncio
from dotenv import load_dotenv
from langchain.agents import AgentType, initialize_agent

# from langchain_community.agent_toolkits import O365Toolkit
from gpt_assistant.tools.office365.toolkit import O365Toolkit
from langchain_openai import OpenAI

from bot_lib import App, Handler, HandlerDisplayMode

# import os

#####################

# from utils.auth import authenticateGoogleUser
# from googleApi.calendar import Calendar


class MyApp(App):
    def __init__(self, plugins, **kwargs):
        super().__init__(plugins=plugins, **kwargs)
        self.toolkit = O365Toolkit()
        tools = self.toolkit.get_tools()
        llm = OpenAI(temperature=0)
        self.agent = initialize_agent(
            tools=tools,
            llm=llm,
            verbose=True,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        )

    def invoke(self, user_id: str, input_str: str) -> str:
        # creds = authenticateGoogleUser()
        # agent.run("Can you schedule a 30 minute meeting with a sentient parrot to discuss research collaborations in 2 hours")
        # res = agent.run("send an email to ershov.k@outlook.com saying hello")
        self.toolkit.authenticate(user_id, handle_consent=lambda url: "authorized_url")
        res = self.agent.run(input_str)
        return res  # todo: check type here
