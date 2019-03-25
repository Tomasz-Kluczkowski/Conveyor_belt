import random
from typing import List, Callable

from src.domain_models.common import BaseModel


def infinite_random_choice():
    choices = [1, 2, 3]
    cho = random.choice(choices)
    while True:
        yield cho



class Feeder(BaseModel):
    """
    Use to provide feed for the conveyor belt. If no feed function specified will select random item from components
    list and return every time feed() is called on an instance.
    """
    def __init__(self, components: List, feed_func: Callable = None, id_: str = None):
        super().__init__(id_)
        self.components = components
        self.__feed_func = feed_func if feed_func else self.__default_feed_func

    def __default_feed_func(self):
        return random.choice(self.components)

    def feed(self):
        return self.__feed_func()


