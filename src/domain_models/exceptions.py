class InvalidItemOperation(Exception):
    def __init__(self, item, message=None):
        if message is None:
            message = f"Unable to pick up item: '{item}'."
        super().__init__(message)
