class Element: #class para representar o elemento na fila de prioridade.
    def __init__(self, value, priority):
        self.item = value #valor do elemento
        self.priority = priority # prioridade do elemento

    def __str__(self):
        return str(self.item) + ' ' + str(self.priority)

class PriorityQueue: #class que implementa uma fila de prioridade usando uma lista de elementos.
    def __init__(self):
        self.elements = [] # lista dos elementos

    def is_empty(self): #verificação da lista se esta vazia.
        return len(self.elements) == 0

    def add_element(self, item, priority): #criação de um objeto Element com o seu valor e prioridade.
        element = Element(item, priority)
        self.elements.append(element)

    def delete_element(self): # remoção do elemento de maior prioridade da fila.
        if self.is_empty(): 
            print("Fila Vazia")
            return None
        else:
            self.elements.sort(key=lambda x: x.priority) # lamba extrai a prioridade de cada elemento x.
            removed = self.elements.pop(0)
            return removed.item

    def print_queue(self): #imprime os elementos que estão na fila de prioridade.
        if self.is_empty():
            print("Fila Vazia")
        else:
            for x in self.elements: # impressão  do elemento.
                print(x)


