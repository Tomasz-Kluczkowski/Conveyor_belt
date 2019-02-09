import uuid

from src.typing_definitions.custom_types import TypeId


class BaseModel:
    def __init__(self, id_: TypeId = None):
        self.id = id_ if id_ else uuid.uuid4()
