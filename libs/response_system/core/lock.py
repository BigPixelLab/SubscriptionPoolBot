
class Lock:
    def __init__(self, storage: set[tuple], key: tuple):
        self.storage = storage
        self.key = key

    def is_set(self):
        return self.key in self.storage

    def __enter__(self):
        self.storage.add(self.key)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.storage.remove(self.key)
