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

    def __set_slot_states_to_free(self):
        for slot_number in range(self.config.conveyor_belt_slots):
            self.__slot_states[slot_number] = ConveyorBeltState.FREE

    def __set_slots_to_empty(self):
        for slot_number in range(self.config.conveyor_belt_slots):
            self.enqueue(self.config.empty_code)

    def __check_validity_of_slot_number(self, slot_number: int):
        if slot_number > self.config.conveyor_belt_slots - 1:
            raise ValueError(INVALID_SLOT_NUMBER)

    def check_at_slot(self, slot_number: int) -> Any:
        """
        Checks for item at a conveyor belt slot. If queue is too short we return empty just as you would examining a
        real conveyor belt (without throwing an error).

        Parameters
        ----------
        slot_number
            Slot of the conveyor belt at which we need to check for item.
        Returns
        -------
            Item at the slot_number if present or EMPTY config value. Note that empty can also be a valid value for
            the slot set by the program.
        """
        self.__check_validity_of_slot_number(slot_number)
        try:
            return self.items[slot_number]
        # We return empty as the queue is not yet filled by the feeder.
        except IndexError:
            return self.config.empty_code

    @property
    def slot_states(self):
        return self.__slot_states

    def set_slot_state(self, slot_number: int, state: str):
        """
        Sets slot state at slot_number.
        """
        self.__check_validity_of_slot_number(slot_number)
        self.__slot_states[slot_number] = state

    def get_slot_state(self, slot_number: int) -> Union[str, None]:
        """
        Returns slot state at slot_number or None if not valid slot accessed.
        """
        return self.__slot_states.get(slot_number)

    def is_slot_busy(self, slot_number: int) -> bool:
        return self.get_slot_state(slot_number) == ConveyorBeltState.BUSY

    def is_slot_empty(self, slot_number: int) -> bool:
        return self.items[slot_number] == self.config.empty_code

    def is_slot_free(self, slot_number: int) -> bool:
        return self.get_slot_state(slot_number) == ConveyorBeltState.FREE

    def retrieve_item_from_slot(self, slot_number: int):
        self.__check_validity_of_slot_number(slot_number)
        self.set_slot_state(slot_number=slot_number, state=ConveyorBeltState.BUSY)
        item = self.check_at_slot(slot_number=slot_number)
        self.put_item_in_slot(slot_number=slot_number, item=self.config.empty_code)

        return item

    def put_item_in_slot(self, slot_number: int, item: str):
        self.__check_validity_of_slot_number(slot_number)
        self.set_slot_state(slot_number=slot_number, state=ConveyorBeltState.BUSY)
        self.items[slot_number] = item
