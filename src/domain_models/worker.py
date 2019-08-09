from typing import List, Any, Type

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt, ConveyorBeltState
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig


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

    def take_item(self):
        self.state = WorkerState.PICKING_UP
        self.remaining_time_of_operation = self.operation_times.PICKING_UP

        item_at_slot = self.conveyor_belt.retrieve_item_from_slot(slot_number=self.slot_number)
        self.items.append(item_at_slot)

    def can_pickup_item(self):
        return self.state == WorkerState.IDLE and self.conveyor_belt.is_slot_free(self.slot_number)

    def build_product(self):
        if self.state == WorkerState.READY_FOR_BUILDING:
            self.state = WorkerState.BUILDING
            self.remaining_time_of_operation = WorkerOperationTimes.BUILDING

    def is_operating(self):
        return self.remaining_time_of_operation > 0

    def is_not_operating(self):
        return self.remaining_time_of_operation == 0

    def is_ready_for_building(self):
        return len(self.items) == len(self.config.required_items)

    def check_item_at_slot(self):
        return self.conveyor_belt.check_at_slot(self.slot_number)

    def is_item_required(self):
        item_on_belt = self.check_item_at_slot()
        return item_on_belt not in self.items and item_on_belt in self.config.required_items

    def execute_operation_period(self):
        """
        Reduce remaining_time_of_operation.
        """
        self.remaining_time_of_operation -= 1

    def update_state(self):
        if self.state in [WorkerState.PICKING_UP, WorkerState.DROPPING]:
            self.state = WorkerState.IDLE
            self.conveyor_belt.set_slot_state(self.slot_number, ConveyorBeltState.FREE)
        elif self.state == WorkerState.IDLE and self.is_ready_for_building():
            self.state = WorkerState.READY_FOR_BUILDING
        elif self.state == WorkerState.BUILDING:
            self.state = WorkerState.FINISHED_BUILDING

    def drop_product(self):
        self.state = WorkerState.DROPPING
        self.remaining_time_of_operation = self.operation_times.DROPPING
        self.conveyor_belt.put_item_in_slot(
            slot_number=self.slot_number, item=self.config.product_code)
        self.items = []

    def work(self):
        if self.is_operating():
            self.execute_operation_period()

        if self.is_not_operating():
            self.update_state()

        if self.can_pickup_item() and self.is_item_required():
            self.take_item()

        self.build_product()
        # TODO: HAVE TO CHECK HERE THAT SLOT IS EMPTY (CONTAINS 'E')
        if self.state == WorkerState.FINISHED_BUILDING and self.conveyor_belt.is_slot_free(self.slot_number):
            self.drop_product()

