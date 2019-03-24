from typing import List, Any

from src.domain_models.common import BaseModel

IDLE = 'idle'
PICKING_UP = 'picking_up'
DROPPING = 'dropping'
BUILDING = 'building'


class Worker(BaseModel):
    def __init__(self, required_items: List[Any], name: str = '', id_: str = None):
        super().__init__(id_)
        self.required_items = required_items
        self.name = name
        self.items = []

    def take_item(self, item):
        if len(self.items) < 2 and item in self.required_items:
            self.items.append(item)
