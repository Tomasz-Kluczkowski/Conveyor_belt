from typing import Any

from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig
from src.helpers.data_structures import Queue


class ConveyorBeltState:
    FREE = 'free'
    BUSY = 'busy'


class ConveyorBelt(Queue):
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
        try:
            return self.items[slot_number]
        except IndexError:
            return FactoryFloorConfig.EMPTY

    def set_slot_state(self):
        # TODO: set slot state when worker operates on it - when pick_up/drop is used.
        pass