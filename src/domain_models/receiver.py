from typing import List, Any

from src.domain_models.common import BaseModel
from src.typing_definitions.custom_types import TypeId


class Receiver(BaseModel):
    """
    Use to receive items from the conveyor belt. Stores items in order of appearance and provides methods to obtain
    efficiency statistics for the plant operation.
    """
    def __init__(self, id_: TypeId = None):
        super().__init__(id_)
        self.__received_items: List[Any] = []

    def __repr__(self):
        return f'<Receiver(id={self.id}, received_items={self.received_items})>'

    @property
    def received_items(self):
        return self.__received_items

    def receive(self, item):
        self.__received_items.append(item)
