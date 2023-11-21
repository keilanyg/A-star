"""from tkinter import *
from square import Square
from priority_queue import PriorityQueue
import time
import threading

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

    def __pre_fill_matrix(self): # criação de matriz de objetos Square.
        for y in range(self.size): #loop para percorrer o labirinto
            self.matrix.append([])# criação das linhas do labirinto.
            for x in range(self.size):
                self.matrix[y].append(Square(x=x, y=y)) # criação de um novo nó  

    def __get_square(self, x, y):
        if 0 <= x < self.size and 0 <= y < self.size:
            if self.matrix[y][x]:
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
                cur_square = self.matrix[row][col]
                cur_square.state = "start"
                self.start_position = (col, row)
                self.current_position = self.start_position
                cur_square.g = 0
                cur_square.h = self.__heuristic(self.current_position)
                cur_square.f = cur_square.g + cur_square.h
                self.open_list.add_element(self.start_position, cur_square.f)

        self.__update()

    def __update(self):
        self.canvas.delete("grid")

        if self.state_button:
            self.state_button.destroy()

        for y in range(self.size):
            for x in range(self.size):
                square: Square = self.__get_square(x, y)
                color = {
                    "": "#FFFFFF",
                    "wall": "#000000",
                    "start": "#223d8f",
                    "goal": "#299855",
                    "path": "pink",
                    "visited": "#12907A"
                }[square.state]

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

    def __find_path(self):
        if not self.open_list.is_empty():
            current_square_position = self.open_list.delete_min()
            x, y = current_square_position
            current_square: Square = self.matrix[y][x]

            self.visited_list.add(current_square_position) #marcação do no visitado.

            current_square.visited = True
            if current_square_position != self.start_position:
                current_square.state = "visited"
        
            self.__update()

            if current_square_position == self.goal_position:
                self.__reconstruct_path(current_square)
                return

            neighbors_positions = self.__find_neighbors(current_square_position) #vizinhos validos.

            for neighbor in neighbors_positions: # loop para ignorar os vizinhos visitados.
                if neighbor in self.visited_list:# ignora o vizinho visitado.
                    continue

                neighbor_square = self.__get_square(neighbor[0], neighbor[1]) # obtendo o nó do vizinho.

                if neighbor_square.state == "wall":
                    continue  # Ignore obstáculos
                
                # Calcula o novo custo g para chegar ao vizinho a partir do nó atual.
                g_score = current_square.g + \
                    self.__calculate_g_score(current_square, neighbor_square)
                print('position', (neighbor[0], neighbor[1]))
                print('valores g:', neighbor_square.g, 'h:', neighbor_square.h, 'f:', neighbor_square.f)

                # Se o novo custo g é menor do que o custo g anterior do vizinho
                if g_score < neighbor_square.g:
                    neighbor_square.parent = current_square
                    neighbor_square.g = g_score
                    neighbor_square.h = self.__heuristic(neighbor)
                    neighbor_square.f = neighbor_square.g + neighbor_square.h
                    self.open_list.add_element(neighbor, neighbor_square.f)
                print('valores atualizados g:', neighbor_square.g, 'h:', neighbor_square.h, 'f:', neighbor_square.f)

            self.master.after(200, self.__find_path)
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
                cur_neighbor_square = self.__get_square(new_x, new_y)

                if 0 <= new_x < self.size and 0 <= new_y < self.size and cur_neighbor_square.state != "wall":
                    neighbors.append((new_x, new_y))

        return neighbors

    def __heuristic(self, current):
        x1, y1 = current
        x2, y2 = self.goal_position
        return abs(x1 - x2) + abs(y1 - y2)

    def __calculate_g_score(self, current_square, neighbor_square):
        dx = abs(current_square.x - neighbor_square.x)
        dy = abs(current_square.y - neighbor_square.y)
        if dx == 1 and dy == 1:
            return 14
        else:
            return 10
        
    def animate_path(self, path):
        for position in path:
            x, y = position
            current_square: Square = self.matrix[y][x]
            current_square.state = "path"
            self.__update()
            time.sleep(0.2)

    def __reconstruct_path(self, current_square):
        path = []
        while current_square.parent:
            path.append((current_square.x, current_square.y))
            current_square = current_square.parent
        path.reverse()
        # Inicie a animação em uma thread separada
        threading.Thread(target=self.animate_path, args=(path,)).start()

if __name__ == "__main__":
    size = 10
    interface = Interface()
    interface.draw_interface()
"""

from tkinter import *
from PIL import Image, ImageTk

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = ""
        self.parent = None

class Interface:
    def __init__(self):
        self.master = Tk()
        self.master.title("A*")
        self.grid_size = 10
        self.square_size = 48
        self.start_position = (2, 0)
        self.goal_position = (1, 0)
        self.current_position = self.start_position

        self.canvas = Canvas(self.master, width=900, height=550)
        self.canvas.pack()

        self.background_image = Image.open("imagens/pacman_background.jpg")
        self.background_image = self.background_image.resize((900, 550))
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        self.start_image = Image.open("imagens/pacman.png")
        self.start_photo = ImageTk.PhotoImage(self.start_image)

        self.goal_image = Image.open("imagens/dot.png")
        self.goal_photo = ImageTk.PhotoImage(self.goal_image)

        self.start_image_id = self.canvas.create_image(
            self.start_position[1] * self.square_size + self.square_size / 2,
            self.start_position[0] * self.square_size + self.square_size / 2,
            image=self.start_photo,
            tags="grid"
        )

        self.goal_image_id = self.canvas.create_image(
            self.goal_position[1] * self.square_size + self.square_size / 2,
            self.goal_position[0] * self.square_size + self.square_size / 2,
            image=self.goal_photo,
            tags="grid"
        )

        self.grid_lines()

        self.master.after(1000, self.loop)

    def draw_interface(self):
        self.master.mainloop()

    def pacman(self, position):
        self.canvas.delete(self.start_image_id)
        self.start_image_id = self.canvas.create_image(
            position[1] * self.square_size + self.square_size / 2,
            position[0] * self.square_size + self.square_size / 2,
            image=self.start_photo,
            tags="grid"
        )

    def goal(self, position):
        self.canvas.delete(self.goal_image_id)
        self.goal_image_id = self.canvas.create_image(
            position[1] * self.square_size + self.square_size / 2,
            position[0] * self.square_size + self.square_size / 2,
            image=self.goal_photo,
            tags="grid"
        )

    def update_positions(self):
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        # Update Pac-Man position
        self.current_position = (
            (self.current_position[0] + 2) % self.grid_size,
            self.current_position[1]
        )

        # Update goal position
        self.goal_position = (
            (self.goal_position[0] + 1) % self.grid_size,
            self.goal_position[1]
        )

    def loop(self):
        self.update_positions()

        # Draw Pac-Man and goal based on updated positions
        self.pacman(self.current_position)
        self.goal(self.goal_position)

        self.master.after(1000, self.loop)

    def grid_lines(self):
        for i in range(1, self.grid_size):
            x = i * self.square_size
            self.canvas.create_line(x, 0, x, self.square_size * self.grid_size, fill="black", tags="grid")
            y = i * self.square_size
            self.canvas.create_line(0, y, self.square_size * self.grid_size, y, fill="black", tags="grid")

if __name__ == "__main__":
    interface = Interface()
    interface.draw_interface()