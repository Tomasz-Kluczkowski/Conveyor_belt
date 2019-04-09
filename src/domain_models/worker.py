from typing import List, Any

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt


class WorkerState:
    IDLE = 'idle'
    PICKING_UP = 'picking_up'
    DROPPING = 'dropping'
    BUILDING = 'building'
    READY_FOR_BUILDING = 'ready_for_building'
    FINISHED_BUILDING = 'finished_building'


class Worker(BaseModel):
    def __init__(self,
                 conveyor_belt: ConveyorBelt,
                 required_items: List[Any],
                 slot: int,
                 time_to_build: int,
                 name: str = '',
                 id_: str = None):
        super().__init__(id_)
        self.conveyor_belt = conveyor_belt
        self.required_items = required_items
        self.slot = slot
        self.time_to_build = time_to_build
        self.name = name
        self.items = []
        self.state = WorkerState.IDLE
        self.time_building = 0

    def is_ready_for_building(self):
        return len(self.items) == len(self.required_items)

    def is_item_pickable(self, item):
        return item not in self.items and item in self.required_items

    def take_item(self, item):
        if self.is_item_pickable(item):
            self.state = WorkerState.PICKING_UP
            # TODO: before we can pickup here we need to make sure slot is not busy and that we use conveyor belt
            #  method for pickup/drop - this is wrong as just appends item, but does not remove it from the conveyor belt!!!
            self.items.append(item)

    def work(self):
        if self.state == WorkerState.READY_FOR_BUILDING:
            pass
        elif self.state == WorkerState.IDLE:
            # TODO: this must be a peek type check
            item_on_belt = self.conveyor_belt.check_at_slot(self.slot)
            self.take_item(item_on_belt)


