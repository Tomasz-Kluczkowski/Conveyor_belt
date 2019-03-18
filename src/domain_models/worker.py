from typing import List, Any

from src.domain_models.common import BaseModel
from src.domain_models.exceptions import InvalidItemOperation


class Worker(BaseModel):
    def __init__(self, required_items: List[Any], name: str = '', id_: str = None):
        super().__init__(id_)
        self.required_items = required_items
        self.name = name
        self.left = None
        self.right = None

    def take_item(self, item):
        if self.left is None:
            self.left = item
        elif self.right is None:
            self.right = item
        else:
            raise InvalidItemOperation(item=item)
