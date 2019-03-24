from typing import List

from src.domain_models.common import BaseModel
from src.domain_models.worker import Worker


class WorkerPair(BaseModel):
    def __init__(self, workers: List[Worker], id_: str = None):
        super().__init__(id_)
        self.workers = workers
