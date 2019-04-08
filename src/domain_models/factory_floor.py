from typing import List

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt
from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.domain_models.worker import Worker, WorkerState
from src.domain_models.worker_pair import WorkerPair
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig
from src.exceptions.exceptions import FactoryConfigError
from src.exceptions.messages import WRONG_FACTORY_CONFIG, INSUFFICIENT_FEED_INPUT
from src.helpers.data_structures import Queue


class FactoryFloor(BaseModel):
    """
    This is the controller of the entire operation. It will navigate the production line.
    By default the number of pairs matches the number of slots on the belt.
    """
    def __init__(self,
                 num_slots: int,
                 feeder: Feeder = None,
                 receiver: Receiver = None,
                 conveyor_belt: Queue = None,
                 num_pairs: int = None,
                 config: FactoryFloorConfig = None,
                 id_: str = None):
        super().__init__(id_)
        if num_pairs and num_pairs > num_slots:
            raise FactoryConfigError(WRONG_FACTORY_CONFIG)
        self.num_slots = num_slots
        self.num_pairs = num_pairs or num_slots
        self.worker_pairs: List[WorkerPair] = []
        self.receiver = receiver if receiver else Receiver()
        self.feeder = feeder if feeder else Feeder()
        self.conveyor_belt = conveyor_belt if conveyor_belt else ConveyorBelt()
        self.config = config if config else FactoryFloorConfig
        self.time = 0

        self.add_worker_pairs()

    def add_worker_pairs(self):
        """
        Creates a WorkerPair per num_pairs. Each worker pair is assigned to a slot on the conveyor belt.
        """
        for slot in range(self.num_pairs):
            workers = [
                Worker(
                    conveyor_belt=self.conveyor_belt, required_items=self.config.REQUIRED_ITEMS, slot=slot
                ) for slot in range(2)
            ]
            worker_pair = WorkerPair(workers=workers, slot=slot)
            self.worker_pairs.append(worker_pair)

    def push_item_to_receiver(self):
        """
        Moves last item on the belt to the receiver when the belt is full.
        """
        if self.conveyor_belt.size == self.num_slots:
            item_to_receive = self.conveyor_belt.dequeue()
            self.receiver.receive(item_to_receive)

    def add_new_item_to_belt(self):
        """
        Adds new item to the conveyor belt.
        """
        if self.conveyor_belt.size < self.num_slots:
            new_belt_item = self.feeder.feed()
            self.conveyor_belt.enqueue(new_belt_item)

    def run_belt(self):
        """
        Main event loop.
        """
        for step in range(self.config.NUM_STEPS):
            # move farthest item on belt to the receiver if line full
            self.push_item_to_receiver()

            # get item from the feeder onto the belt
            try:
                self.add_new_item_to_belt()
            except StopIteration:
                raise FactoryConfigError(INSUFFICIENT_FEED_INPUT)

            # make each pair work
            for worker_pair in self.worker_pairs:
                item_on_belt = self.conveyor_belt.check_at_slot(worker_pair.slot)
            #     now find who in the pair can actually work (so check the status)
                for worker in worker_pair.workers:
                    worker.work()

            #      if worker is idle, pick up stuff
            # finally always increase time at the end of each tick
            self.time += 1
