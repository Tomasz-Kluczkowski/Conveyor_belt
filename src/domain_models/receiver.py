from typing import List, Any

from src.domain_models.common import BaseModel


class Receiver(BaseModel):
    """
    Use to receive items from the conveyor belt. Stores items in order of appearance and provides methods to obtain
    efficiency statistics for the plant operation.
    """
    def __init__(self):
        self.__received_items: List[Any] = []

    @property
    def received_items(self):
        return self.__received_items

    def receive(self, item):
        self.__received_items.append(item)
