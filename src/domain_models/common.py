import uuid


class BaseModel:
    def __init__(self, id_: str = None):
        self.id = id_ if id_ else uuid.uuid4()

    def __repr__(self):
        attributes = ', '.join([f'{field}={value}' for field, value in self.__dict__.items()])
        representation = f'<{self.__class__.__name__}({attributes})>'
        return representation
