from typing import Any

from src.exceptions.messages import INVALID_SLOT_NUMBER
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig
from src.helpers.data_structures import Queue


class ConveyorBeltState:
    FREE = 'free'
    BUSY = 'busy'


class ConveyorBelt(Queue):
    def __init__(self, num_slots: int):
        super(). __init__()
        self.num_slots = num_slots
        self.__slot_states = {}

    def __check_validity_of_slot_number(self, slot_number: int):
        if slot_number > self.num_slots:
            raise ValueError(INVALID_SLOT_NUMBER)

    def check_at_slot(self, slot_number: int) -> Any:
        """
        Checks for item at a conveyor belt slot. If queue is too short we return empty just as you would examining a
        real conveyor belt.
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
            return FactoryFloorConfig.EMPTY

    @property
    def slot_states(self):
        return self.__slot_states

    def set_slot_state(self, slot_number: int, state: str):
        self.__check_validity_of_slot_number(slot_number)
        self.__slot_states[slot_number] = state
