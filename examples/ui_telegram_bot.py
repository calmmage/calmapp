"""
Goal of this file:
given an app that has a simple text-based interface, we want to create a bot-lib telegram bot interface for it
app will have .invoke() method that takes a string and returns a string
"""

from calmapp.ui.ui_telegram_bot import (
    take_care_of_everything,
    AppInvokeHandler,
    App,
)

if __name__ == "__main__":
    take_care_of_everything(AppInvokeHandler, App)
