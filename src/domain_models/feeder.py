import random
from typing import List, Callable

from src.domain_models.common import BaseModel
from src.typing_definitions.custom_types import TypeId


class Feeder(BaseModel):
    """
    Use to provide feed for the conveyor belt. If no feed function specified will select random item from components
    list and return every time feed() is called on an instance.
    """
    def __init__(self, components: List, feed_func: Callable = None, id_: TypeId = None):
        super().__init__(id_)
        self.components = components
        self.__feed_func = feed_func if feed_func else self.__default_feed_func

    def __repr__(self):
        return f'<Feeder(id={self.id}, components={self.components}, feed_func={self.__feed_func.__name__})>'

    def __default_feed_func(self):
        return random.choice(self.components)

    def feed(self):
        return self.__feed_func()
