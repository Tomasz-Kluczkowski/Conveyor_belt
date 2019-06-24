from typing import List, Any, Type

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt, ConveyorBeltState


class WorkerState:
    IDLE = 'idle'
    PICKING_UP = 'picking_up'
    DROPPING = 'dropping'
    BUILDING = 'building'
    READY_FOR_BUILDING = 'ready_for_building'
    FINISHED_BUILDING = 'finished_building'


class WorkerOperationTimes:
    PICKING_UP = 1
    DROPPING = 1
    BUILDING = 4


class Worker(BaseModel):
    def __init__(self,
                 conveyor_belt: ConveyorBelt,
                 required_items: List[Any],
                 slot_number: int,
                 operation_times: Type[WorkerOperationTimes],
                 name: str = '',
                 id_: str = None):
        super().__init__(id_)
        self.conveyor_belt = conveyor_belt
        self.required_items = required_items
        self.slot_number = slot_number
        self.operation_times = operation_times
        self.name = name
        self.items = []
        self.state = WorkerState.IDLE
        self.elapsed_time_of_operation = 0

    def is_ready_for_building(self):
        return len(self.items) == len(self.required_items)

    def is_item_required(self, item):
        return item not in self.items and item in self.required_items

    def take_item(self, item):
        if self.is_item_required(item) and self.conveyor_belt.is_slot_free(self.slot_number):
            self.state = WorkerState.PICKING_UP
            self.conveyor_belt.set_slot_state(self.slot_number, ConveyorBeltState.BUSY)
            self.items.append(item)

    def work(self):
        if self.state == WorkerState.READY_FOR_BUILDING:
            pass

        elif self.state == WorkerState.IDLE:
            item_on_belt = self.conveyor_belt.check_at_slot(self.slot_number)
            self.take_item(item_on_belt)


