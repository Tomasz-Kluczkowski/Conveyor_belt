from typing import List

from src.domain_models.common import BaseModel
from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.domain_models.worker import Worker
from src.domain_models.worker_pair import WorkerPair
from src.factory_configuration.factory_configuration import REQUIRED_ITEMS, NUM_STEPS
from src.helpers.data_structures import Queue


class ConveyorBelt(BaseModel):
    """
    This is the controller of the entire operation. It will navigate the production line.
    By default the number of pairs matches the number of slots on the belt.
    """
    def __init__(self, feeder: Feeder, receiver: Receiver, num_slots: int, num_pairs: int = None, id_: str = None):
        super().__init__(id_)
        self.feeder = feeder
        self.receiver = receiver
        self.num_slots = num_slots
        if num_pairs and num_pairs > num_slots:
            raise ValueError(
                'Improperly configured ConveyorBelt - num_pairs cannot exceed num_slots.'
            )
        self.num_pairs = num_pairs or num_slots
        self.worker_pairs: List[WorkerPair] = []
        self.items_on_belt: Queue = Queue()

        self.add_worker_pairs()

    def add_worker_pairs(self):
        """
        Creates a WorkerPair per num_pairs.
        """
        for slot in range(self.num_pairs):
            workers = [Worker(required_items=REQUIRED_ITEMS) for _ in range(2)]
            worker_pair = WorkerPair(workers=workers)
            self.worker_pairs.append(worker_pair)

    def push_item_to_receiver(self):
        """
        Moves last item on the belt to the receiver when the belt is full.
        """
        if self.items_on_belt.size == self.num_slots:
            item_to_receive = self.items_on_belt.dequeue()
            self.receiver.receive(item_to_receive)

    def add_new_item_to_belt(self):
        """
        Adds new item to the conveyor belt.
        """
        if self.items_on_belt.size < self.num_slots:
            new_belt_item = self.feeder.feed()
            self.items_on_belt.enqueue(new_belt_item)

    def run_belt(self):
        """
        Main event loop.
        """
        for step in NUM_STEPS:
            # move farthest item on belt to the receiver if line full
            self.push_item_to_receiver()

            # get item from the feeder onto the belt
            self.add_new_item_to_belt()
