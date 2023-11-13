class Element:
    def __init__(self, value, priority):
        self.item = value
        self.priority = priority

    def __str__(self):
        return str(self.item) + ' ' + str(self.priority)

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def is_empty(self):
        return len(self.elements) == 0

    def add_element(self, item, priority):
        element = Element(item, priority)
        self.elements.append(element)

    def delete_element(self):
        if self.is_empty():
            print("Queue is empty")
            return None
        else:
            self.elements.sort(key=lambda x: x.priority)
            removed = self.elements.pop(0)
            return removed.item

    def print_queue(self):
        if self.is_empty():
            print("Queue is empty")
        else:
            for x in self.elements:
                print(x, ": pri", x.priority)


