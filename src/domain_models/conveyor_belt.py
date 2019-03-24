from src.domain_models.common import BaseModel
from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver
from src.domain_models.worker import Worker
from src.domain_models.worker_pair import WorkerPair
from src.factory_configuration.factory_configuration import REQUIRED_ITEMS


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
        self.worker_pairs = []
        self.items_on_belt = []
        # create WorkerPairs
        self.add_worker_pairs()

    def add_worker_pairs(self):
        """
        Created a worker pair pair num_slots.
        """
        for slot in range(self.num_pairs):
            workers = [Worker(required_items=REQUIRED_ITEMS) for _ in range(2)]
            worker_pair = WorkerPair(workers=workers)
            self.worker_pairs.append(worker_pair)

    # def run_belt(self):
    #     """
    #     Main event loop.
    #     """
    #
