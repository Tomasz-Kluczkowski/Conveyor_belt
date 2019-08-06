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

    def pickup_item(self):
        item_on_belt = self.conveyor_belt.check_at_slot(self.slot_number)

        if self.is_item_required(item_on_belt):
            self.take_item(item_on_belt)

    def build_product(self):
        if self.state == WorkerState.READY_FOR_BUILDING:
            self.state = WorkerState.BUILDING
            self.remaining_time_of_operation = WorkerOperationTimes.BUILDING

    def is_ready_for_building(self):
        return len(self.items) == len(self.config.required_items)

    def is_item_required(self, item):
        return item not in self.items and item in self.config.required_items

    def take_item(self, item):
        self.state = WorkerState.PICKING_UP
        self.remaining_time_of_operation = self.operation_times.PICKING_UP

        self.conveyor_belt.set_slot_state(self.slot_number, ConveyorBeltState.BUSY)
        self.items.append(item)
        self.conveyor_belt.put_item_in_slot(slot_number=self.slot_number, item=self.config.empty_code)

    def execute_operation_period(self):
        """
        Reduce remaining_time_of_operation if greater than zero. If that caused it to be equal to zero
        change state to idle - operation has completed.
        """
        if self.remaining_time_of_operation > 0:
            self.remaining_time_of_operation -= 1

        # TODO: check if this can be moved out into a separate method
        if self.remaining_time_of_operation == 0:
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
        self.execute_operation_period()

        if self.state == WorkerState.IDLE and self.conveyor_belt.is_slot_free(self.slot_number):
            self.pickup_item()

        self.build_product()
        # TODO: HAVE TO CHECK HERE THAT SLOT IS EMPTY (CONTAINS 'E')
        if self.state == WorkerState.FINISHED_BUILDING and self.conveyor_belt.is_slot_free(self.slot_number):
            self.drop_product()

