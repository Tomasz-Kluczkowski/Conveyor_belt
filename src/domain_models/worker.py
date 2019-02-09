from src.domain_models.common import BaseModel
from src.typing_definitions.custom_types import TypeId


class Worker(BaseModel):
    def __init__(self, name: str = '', id_: TypeId = None):
        super().__init__(id_)
        self.name = name
        self.left = None
        self.right = None

    def __repr__(self):
        return f"<Worker(id={self.id}, name='{self.name}', left={self.left}, right={self.right})>"
