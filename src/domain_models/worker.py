from typing import List, Any

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt


class WorkerState:
    IDLE = 'idle'
    PICKING_UP = 'picking_up'
    DROPPING = 'dropping'
    BUILDING = 'building'


class Worker(BaseModel):
    def __init__(self, conveyor_belt: ConveyorBelt, required_items: List[Any], slot: int, name: str = '', id_: str = None):
        super().__init__(id_)
        self.conveyor_belt = conveyor_belt
        self.required_items = required_items
        self.slot = slot
        self.name = name
        self.items = []
        self.state = WorkerState.IDLE

    def work(self):
        if self.state == WorkerState.IDLE:
            pass

    def take_item(self, item):
        if len(self.items) < 2 and item not in self.items and item in self.required_items:
            self.items.append(item)
