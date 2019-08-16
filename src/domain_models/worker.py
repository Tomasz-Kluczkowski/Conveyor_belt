from typing import List, Any, Type

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt, ConveyorBeltState
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig


class WorkerState:
    IDLE = 'idle'
    PICKING_UP = 'picking_up'
    DROPPING = 'dropping'
    BUILDING = 'building'
    FINISHED_BUILDING = 'finished_building'


class WorkerOperationTimes:
    PICKING_UP = 1
    DROPPING = 1
    BUILDING = 4


class Worker(BaseModel):
    def __init__(self,
                 config: FactoryFloorConfig,
                 conveyor_belt: ConveyorBelt,
                 slot_number: int,
                 operation_times: Type[WorkerOperationTimes],
                 name: str = '',
                 id_: str = None):
        super().__init__(id_)
        self.config = config
        self.conveyor_belt = conveyor_belt
        self.slot_number = slot_number
        self.operation_times = operation_times
        self.name = name
        self.items = []
        self.state = WorkerState.IDLE
        self.remaining_time_of_operation = 0

    def pickup_item(self):
        self.remaining_time_of_operation = self.operation_times.PICKING_UP

        item_at_slot = self.conveyor_belt.retrieve_item_from_slot(slot_number=self.slot_number)
        self.items.append(item_at_slot)

    def can_pickup_item(self):
        return self.conveyor_belt.is_slot_free(self.slot_number)

    def can_drop_product(self):
        return self.conveyor_belt.is_slot_free(self.slot_number) and self.conveyor_belt.is_slot_empty(self.slot_number)

    def build_product(self):
        self.remaining_time_of_operation = WorkerOperationTimes.BUILDING

    def is_operating(self):
        return self.remaining_time_of_operation > 0

    def is_not_operating(self):
        return self.remaining_time_of_operation == 0

    def is_ready_for_building(self):
        return len(self.items) == len(self.config.required_items)

    def is_item_required(self):
        item_on_belt = self.conveyor_belt.check_item_at_slot(self.slot_number)
        return item_on_belt not in self.items and item_on_belt in self.config.required_items

    def reduce_operation_time(self):
        self.remaining_time_of_operation -= 1

    def update_state(self):
        if self.state in [WorkerState.PICKING_UP, WorkerState.DROPPING]:
            if self.is_not_operating():
                self.state = WorkerState.IDLE
                self.conveyor_belt.confirm_operation_at_slot_finished(slot_number=self.slot_number)

        if self.state == WorkerState.IDLE:
            if self.can_pickup_item() and self.is_item_required():
                self.state = WorkerState.PICKING_UP
                self.pickup_item()

            elif self.is_ready_for_building():
                self.state = WorkerState.BUILDING
                self.build_product()

        if self.state == WorkerState.BUILDING:
            if self.is_not_operating():
                self.state = WorkerState.FINISHED_BUILDING

        elif self.state == WorkerState.FINISHED_BUILDING:
            if self.can_drop_product():
                self.state = WorkerState.DROPPING
                self.drop_product()

    def drop_product(self):
        self.remaining_time_of_operation = self.operation_times.DROPPING
        self.conveyor_belt.put_item_in_slot(
            slot_number=self.slot_number, item=self.config.product_code)
        self.items = []

    def work(self):
        # TODO: reduce time after update state and change state transitions to simpler based in diagram
        #  assuming that it will keep working.
        if self.is_operating():
            self.reduce_operation_time()

        self.update_state()
