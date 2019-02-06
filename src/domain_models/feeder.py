import random
import uuid
from typing import List, Callable
from src.typing_definitions.custom_types import TypeId


class Feeder:
    """
    Use to provide feed for the conveyor belt. If no feed function specified will select random item from components
    list and return every time feed() is called on an instance.
    """
    def __init__(self, components: List, feed_func: Callable = None, id: TypeId = None):
        self.id = id if id else uuid.uuid4()
        self.components = components
        self.__feed_func = feed_func if feed_func else self.__basic_feed_func

    def __repr__(self):
        return f'<Feeder(id={self.id}, components={self.components}, feed_func={self.__feed_func.__name__})>'

    def __basic_feed_func(self):
        return random.choice(self.components)

    def feed(self):
        return self.__feed_func()
