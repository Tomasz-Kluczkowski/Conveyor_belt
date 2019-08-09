from typing import Any, Union

from src.exceptions.messages import INVALID_SLOT_NUMBER
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig
from src.helpers.data_structures import Queue


class ConveyorBeltState:
    FREE = 'free'
    BUSY = 'busy'


class ConveyorBelt(Queue):
    def __init__(self, config: FactoryFloorConfig):
        super(). __init__()
        self.config = config
        self.__slot_states = {}
        self.__set_slot_states_to_free()
        self.__set_slots_to_empty()

    @property
    def slot_states(self):
        return self.__slot_states

    def check_item_at_slot(self, slot_number: int) -> Any:
        """
        Returns item at a conveyor belt slot.

        Parameters
        ----------
        slot_number
            Slot of the conveyor belt at which we need to check for item.
        Returns
        -------
            Item at the slot_number.
        """
        # TODO: Make items private in the Queue. give necessary access methods if needed.
        return self.items[slot_number]

    def put_item_in_slot(self, slot_number: int, item: str):
        self.__set_slot_state(slot_number=slot_number, state=ConveyorBeltState.BUSY)
        self.items[slot_number] = item

    def confirm_operation_finished(self, slot_number: int):
        self.__set_slot_state(slot_number=slot_number, state=ConveyorBeltState.FREE)

    def is_slot_busy(self, slot_number: int) -> bool:
        return self.__get_slot_state(slot_number) == ConveyorBeltState.BUSY

    def is_slot_empty(self, slot_number: int) -> bool:
        return self.items[slot_number] == self.config.empty_code

    def is_slot_free(self, slot_number: int) -> bool:
        return self.__get_slot_state(slot_number) == ConveyorBeltState.FREE

    def retrieve_item_from_slot(self, slot_number: int):
        self.__set_slot_state(slot_number=slot_number, state=ConveyorBeltState.BUSY)
        item = self.check_item_at_slot(slot_number=slot_number)
        self.put_item_in_slot(slot_number=slot_number, item=self.config.empty_code)

        return item

    def __set_slot_states_to_free(self):
        for slot_number in range(self.config.conveyor_belt_slots):
            self.__slot_states[slot_number] = ConveyorBeltState.FREE

    def __set_slots_to_empty(self):
        for slot_number in range(self.config.conveyor_belt_slots):
            self.enqueue(self.config.empty_code)

    def __set_slot_state(self, slot_number: int, state: str):
        """
        Sets slot state at slot_number.
        """
        self.__slot_states[slot_number] = state

    def __get_slot_state(self, slot_number: int) -> Union[str, None]:
        """
        Returns slot state at slot_number or None if not valid slot accessed.
        """
        return self.__slot_states.get(slot_number)
