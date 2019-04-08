from typing import List

from src.domain_models.common import BaseModel
from src.domain_models.worker import Worker


class WorkerPair(BaseModel):
    def __init__(self, slot: int, workers: List[Worker], id_: str = None):
        """

        Parameters
        ----------
        slot
            Slot on the conveyor belt to which this WorkerPair is assigned to.
        workers
            List of workers in this pair.
        id_
            Identifier of the pair.
        """
        super().__init__(id_)
        self.workers = workers
        self.slot = slot
