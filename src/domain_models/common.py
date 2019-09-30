class BaseModel:
    def __repr__(self):
        attributes = ', '.join([f'{field}={value}' for field, value in self.__dict__.items()])
        representation = f'<{self.__class__.__name__}({attributes})>'
        return representation
