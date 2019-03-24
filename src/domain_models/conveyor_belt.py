from src.domain_models.common import BaseModel
from src.domain_models.feeder import Feeder
from src.domain_models.receiver import Receiver


class ConveyorBelt(BaseModel):
    """
    This is the controller of the entire operation. It will navigate the production line.
    """
    def __init__(self, feeder: Feeder, receiver: Receiver, id_: str = None):
        super().__init__(id_)
        self.slots = []
        self.worker_pairs = []
        self.feeder = feeder
        self.receiver = receiver
