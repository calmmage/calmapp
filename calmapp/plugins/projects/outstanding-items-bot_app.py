import os

from calmapp import App
from dotenv import load_dotenv

from outstanding_items_bot.todo.todo_item_repository import TodoItemRepository, TodoItem

load_dotenv()


class MyApp(App):
    """This is an amazing application that I developed in my free time! For now it just exists, and that is good!"""

    name: str = "Outstanding Items Bot"
    # Sample
    start_message = "Hello! I am {name}. {description}"
    # Sample help message
    help_message = "Help! I need somebody! Help! Not just anybody! Help! You know I need someone! Help!"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.item_repository = TodoItemRepository(root_folder=self.app_data_path / "items")

        items = self.item_repository.get_all_items()
        self.items = {item.id: item for item in items}
        self.keys_by_item_id = {item.id: item.keys[0] for item in items}  # item id -> item key / shortcut
        self.occupied_keys = set(item.keys[0] for item in items)

        self.items_by_key = {key: item for item in items for key in item.keys}

        self.last_item_id = None
        self.debug = os.getenv("DEBUG_MODE")

    @property
    def description(self):
        return self.__doc__

    def invoke(self, input_str):
        return input_str

    def dummy_command(self):
        return "Hey! I am a dummy"

    def assign_key(self, description):
        # take first word
        key = description.strip().split(" ", 1)[0]
        # check if key is already used
        if key in self.occupied_keys:
            # add a number to the end of the key
            i = 1
            while True:
                new_key = f"{key} {i}"
                if new_key not in self.occupied_keys:
                    key = new_key
                    break
                i += 1
        self.occupied_keys.add(key)
        return key

    def add_item(self, description):
        key = self.assign_key(description)
        title, description = (description + "\n").split("\n", 1)
        item = TodoItem(
            title=title,
            description=description.strip(),
            due_date=None,
            completed=False,
            next_reminder=None,
            category=None,
            keys=[key],
        )
        self.item_repository.save(item)
        self.items[item.id] = item
        self.items_by_key[key] = item
        self.keys_by_item_id[item.id] = key
        return item

    def get_item(self, key):
        # first try to load by id
        if key in self.items:
            return self.items.get(key)
        # then try to load by key
        if key in self.items_by_key:
            return self.items_by_key.get(key)
        # then fuzzy match key
        key = self.fuzzy_match_key(key)
        return self.items_by_key.get(key)

    def get_all_items(self, include_completed=False):
        return [item for item in self.items.values() if include_completed or not item.completed]

    def has_item(self, key):
        if key in self.items:
            return True
        key = self.fuzzy_match_key(key)
        return key in self.items_by_key

    def fuzzy_match_key(self, key):
        candidates = [k for k in self.items_by_key if k.startswith(key)]
        if len(candidates) == 1:
            return candidates[0]
        return key

    def delete_item(self, key=None):
        if key is None:
            key = self.last_item_id
        key = self.fuzzy_match_key(key)
        item = self.items_by_key.get(key)
        if item:
            del self.items[item.id]
            del self.items_by_key[key]
            del self.keys_by_item_id[item.id]
            self.occupied_keys.remove(key)
            self.item_repository.delete(item.id)
            return True
        return False

    def complete(self, key):
        key = self.fuzzy_match_key(key)
        item = self.items_by_key.get(key)
        if item:
            item.completed = True
            self.item_repository.save(item)
            return True
        return False
