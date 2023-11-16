from tkinter import *
from node import Node
from priority_queue import PriorityQueue

def generate_matrix(size: int):
    import numpy as np
    matrix = np.full((size, size), 1)
    print(matrix)
    return matrix

class Interface:
    def __init__(self, matrix=None):
        self.matrix = []
        self.master = Tk()
        self.master.title("A* Maze Solver")
        self.square_dimension = 48
        self.size = 10
        self.current_state = "wall"
        self.__pre_fill_matrix()

        self.canvas = Canvas(self.master, width=480, height=500)
        self.canvas.bind("<Button-1>", self.__set_square_color)
        self.canvas.pack()

        self.state_button = None
        self.start_position = None
        self.goal_position = None
        self.open_list = PriorityQueue()
        self.current_position = None
        self.after_id = None  # ID do agendador do Tkinter
        self.visited_list = set()
        self.__update()

    def __pre_fill_matrix(self):
        for y in range(self.size):
            self.matrix.append([])
            for x in range(self.size):
                self.matrix[y].append(Node(x=x, y=y))

    def __get_node(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.matrix[y][x]

    def draw_interface(self):
        self.master.mainloop()

    def __set_goal(self):
        self.current_state = "goal"

    def __set_start(self):
        self.current_state = "start"

    def __set_square_color(self, event):
        row = event.x // self.square_dimension
        col = event.y // self.square_dimension

        if self.current_state == "wall":
            self.matrix[row][col].state = "wall"
        elif self.current_state == "goal":
            if self.goal_position is None:
                self.matrix[row][col].state = "goal"
                self.goal_position = (col, row)
        elif self.current_state == "start":
            if self.start_position is None:
                cur_node = self.matrix[row][col]
                cur_node.state = "start"
                self.start_position = (col, row)
                self.current_position = self.start_position
                cur_node.g = 0
                cur_node.h = self.__heuristic(self.current_position)
                cur_node.f = cur_node.g + cur_node.h
                self.open_list.add_element(self.start_position, cur_node.f)

        self.__update()

    def __update(self):
        self.canvas.delete("grid")

        if self.state_button:
            self.state_button.destroy()

        for y in range(self.size):
            for x in range(self.size):
                node: Node = self.__get_node(x, y)
                color = {
                    "": "#FFFFFF",
                    "wall": "#000000",
                    "start": "#223d8f",
                    "goal": "#299855",
                    "path": "pink",
                    "parent": "purple",
                    "visited": "#12907A"
                }[node.state]

                self.canvas.create_rectangle(y * self.square_dimension,
                                             x * self.square_dimension,
                                             (y + 1) * self.square_dimension,
                                             (x + 1) * self.square_dimension,
                                             fill=color,
                                             outline="black",
                                             tags="grid"
                                             )

        if self.current_state == "wall":
            self.state_button = Button(
                self.master, text="Selecione a posição do objetivo", command=self.__set_goal)
            self.state_button.pack()
        elif self.current_state == "goal":
            self.state_button = Button(
                self.master, text="Selecione a posição inicial", command=self.__set_start)
            self.state_button.pack()
        elif self.current_state == "start":
            self.state_button = Button(
                self.master, text="Iniciar algoritmo", command=self.__find_path)
            self.state_button.pack()

    def __start_algorithm(self):
        self.__find_path()  # Inicia o algoritmo diretamente

    def __find_path(self):
        if not self.open_list.is_empty():
            current_node_position = self.open_list.delete_element()
            x, y = current_node_position
            current_node: Node = self.matrix[y][x]

            self.visited_list.add(current_node_position)

            current_node.visited = True
            if current_node_position != self.start_position:
                current_node.state = "visited"
            self.canvas.create_rectangle(y * self.square_dimension,
                                         x * self.square_dimension,
                                         (y + 1) * self.square_dimension,
                                         (x + 1) * self.square_dimension,
                                         fill="yellow",  # Cor de destaque
                                         outline="black",
                                         tags="grid"
                                         )
            self.__update()
            # time.sleep(0.2)

            if current_node_position == self.goal_position:
                self.__reconstruct_path(current_node)
                return

            neighbors_positions = self.__find_neighbors(current_node_position)

            for neighbor in neighbors_positions:
                if neighbor in self.visited_list:
                    continue

                neighbor_node = self.__get_node(neighbor[0], neighbor[1])

                if neighbor_node.state == "wall":
                    continue  # Ignore obstáculos

                # Calcula o novo custo g para chegar ao vizinho a partir do nó atual.
                g_score = current_node.g + self.__calculate_g_score(current_node, neighbor_node)

                # Se o vizinho não está na lista aberta ou o novo custo g é menor que o custo g anterior
                if neighbor_node.g == float('inf') or g_score < neighbor_node.g:
                    neighbor_node.parent = current_node
                    neighbor_node.g = g_score
                    neighbor_node.h = self.__heuristic(neighbor)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    self.open_list.add_element(neighbor, neighbor_node.f)

            self.master.after(200, self.__find_path)  # Agende a próxima chamada
        else:
            print("No path found")

    def __find_neighbors(self, current):
        x, y = current
        neighbors = []

        for n_x in [-1, 0, 1]:
            for n_y in [-1, 0, 1]:
                if n_x == 0 and n_y == 0:
                    continue

                new_x, new_y = x + n_x, y + n_y
                cur_neighbor_node = self.__get_node(new_x, new_y)

                if 0 <= new_x < self.size and 0 <= new_y < self.size and cur_neighbor_node.state != "wall":
                    neighbors.append((new_x, new_y))

        return neighbors

    def __heuristic(self, current):
        x1, y1 = current
        x2, y2 = self.goal_position
        return abs(x1 - x2) + abs(y1 - y2)

    def __calculate_g_score(self, current_node, neighbor_node):
        dx = abs(current_node.x - neighbor_node.x)
        dy = abs(current_node.y - neighbor_node.y)
        if dx == 1 and dy == 1:
            return 14
        else:
            return 10

    def __reconstruct_path(self, current_node):
        while current_node.parent:
            current_node.state = "path"
            current_node = current_node.parent
        self.__update()

if __name__ == "__main__":
    size = 10
    interface = Interface()
    interface.draw_interface()