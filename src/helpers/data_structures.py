class Queue:

    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    @property
    def is_empty(self):
        return len(self.items) == 0

    @property
    def size(self):
        return len(self.items)


class MaxSizeQueue(Queue):
    pass
