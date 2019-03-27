import random
from typing import List, Iterable, Union, Sequence

from src.domain_models.common import BaseModel
from src.exceptions.messages import INVALID_FEED_INPUT


class Feeder(BaseModel):
    """
    Use to provide feed for the conveyor belt. If no feed function specified will select random item from components
    list and return every time feed() is called on an instance.
    """
    def __init__(self, components: List, feed_input: Union[Iterable, Sequence] = None, id_: str = None):
        super().__init__(id_)
        self.components = components
        self.__feed_input = self.get_feed_input(feed_input) if feed_input else self.__default_feed_input()

    def __default_feed_input(self):
        while True:
            yield random.choice(self.components)

    @staticmethod
    def get_feed_input(feed_input: Union[Iterable, Sequence]):
        """
        Iterates over and returns items from feed_input.
        """
        if hasattr(feed_input, '__next__'):
            return feed_input
        try:
            feed_iterator = iter(feed_input)
            return feed_iterator
        except TypeError:
            raise TypeError(INVALID_FEED_INPUT.format(object_type=feed_input.__class__.__name__))

    def feed(self):
        return next(self.__feed_input)
