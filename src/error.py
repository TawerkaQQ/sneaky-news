class Missing(Exception):
    def __init__(self, message: str):
        self.message = message

class Duplicate(Exception):
    def __init__(self, message: str):
        self.message = message