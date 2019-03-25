class Queue:

    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.pop(0)

    @property
    def is_empty(self):
        return len(self.items) == 0

    @property
    def size(self):
        return len(self.items)
