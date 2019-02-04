import uuid
from typing import List, Callable
from src.typing_definitions.custom_types import TypeId


class Feeder:
    def __init__(self, components: List, feed_func: Callable, id: TypeId = None):
        self.id = id if id else uuid.uuid4()
        self.components = components
        self.feed_func = feed_func
