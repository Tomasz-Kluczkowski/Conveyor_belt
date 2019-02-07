import uuid
from typing import List, Any
from src.typing_definitions.custom_types import TypeId


class Receiver:
    """
    Use to receive items from the conveyor belt. Stores items in order of appearance and provides methods to obtain
    efficiency statistics for the plant operation.
    """
    def __init__(self, id: TypeId = None):
        self.id = id if id else uuid.uuid4()
        self.__received_items: List[Any] = []

    # def __repr__(self):
    #     return f'<Receiver(id={self.id}, components={self.components}, feed_func={self.__feed_func.__name__})>'
