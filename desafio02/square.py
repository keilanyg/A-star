class Square:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float('inf')
        self.h = 0
        self.f = 0
        self.state = ""
        self.parent = None
        self.neighbors = []