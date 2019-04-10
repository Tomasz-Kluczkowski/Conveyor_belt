from typing import List

from src.domain_models.common import BaseModel
from src.domain_models.conveyor_belt import ConveyorBelt
from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.domain_models.worker import Worker
# from src.domain_models.worker_pair import WorkerPair
from src.factory_floor_configuration.factory_floor_configuration import FactoryFloorConfig
from src.exceptions.exceptions import FactoryConfigError
from src.exceptions.messages import WRONG_FACTORY_CONFIG, INSUFFICIENT_FEED_INPUT


class FactoryFloor(BaseModel):
    def __init__(self,
                 config: FactoryFloorConfig = None,
                 feeder: Feeder = None,
                 receiver: Receiver = None,
                 conveyor_belt: ConveyorBelt = None,
                 num_pairs: int = None,
                 workers: List[Worker] = None,
                 # worker_pairs: List[WorkerPair] = None,
                 id_: str = None):
        super().__init__(id_)

        self.config = config if config else FactoryFloorConfig
        self.feeder = feeder if feeder else Feeder()
        self.receiver = receiver if receiver else Receiver()
        self.conveyor_belt = conveyor_belt if conveyor_belt else ConveyorBelt(num_slots=self.config.CONVEYOR_BELT_SLOTS)
        self.num_pairs = num_pairs or self.conveyor_belt.num_slots
        if num_pairs and num_pairs > self.conveyor_belt.num_slots:
            raise FactoryConfigError(WRONG_FACTORY_CONFIG)
        self.time = 0
        # self.worker_pairs = worker_pairs if worker_pairs else self.add_worker_pairs()
        self.workers = workers if workers else self.add_workers()
    """
    This is the controller of the entire operation. It will navigate the production line.
    By default the number of pairs matches the number of slots on the belt.
    """

    # def add_worker_pairs(self):
    #     """
    #     Creates a WorkerPair per num_pairs. Each worker pair is assigned to a slot on the conveyor belt.
    #     """
    #     worker_pairs = []
    #     for slot in range(self.num_pairs):
    #         workers = [
    #             Worker(
    #                 conveyor_belt=self.conveyor_belt,
    #                 required_items=self.config.REQUIRED_ITEMS,
    #                 time_to_build=self.config.TIME_TO_BUILD,
    #                 slot=slot
    #             ) for _ in range(2)
    #         ]
    #         worker_pair = WorkerPair(workers=workers, slot=slot, conveyor_belt=self.conveyor_belt)
    #         worker_pairs.append(worker_pair)
    #     return worker_pairs

    def add_workers(self):
        """
        Creates a pair of workers per num_pairs. Each worker pair is assigned to a slot on the conveyor belt.
        """
        workers = []
        for slot in range(self.num_pairs):
            for _ in range(2):
                worker = Worker(
                        conveyor_belt=self.conveyor_belt,
                        required_items=self.config.REQUIRED_ITEMS,
                        time_to_build=self.config.TIME_TO_BUILD,
                        slot=slot
                    )
                workers.append(worker)
        return workers

    def push_item_to_receiver(self):
        """
        Moves last item on the belt to the receiver when the belt is full.
        """
        if self.conveyor_belt.size == self.conveyor_belt.num_slots:
            item_to_receive = self.conveyor_belt.dequeue()
            self.receiver.receive(item_to_receive)

    def add_new_item_to_belt(self):
        """
        Adds new item to the conveyor belt.
        """
        if self.conveyor_belt.size < self.conveyor_belt.num_slots:
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
            # for worker_pair in self.worker_pairs:
            # #     now find who in the pair can actually work (so check the status)
            #     for worker in worker_pair.workers:
            #         worker.work()

            #      if worker is idle, pick up stuff
            # finally always increase time at the end of each tick
            self.time += 1
