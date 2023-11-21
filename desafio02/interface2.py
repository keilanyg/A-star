from tkinter import *
from PIL import Image, ImageTk
from square import Square
from priority_queue import PriorityQueue
import threading
import time


class Interface:
    def __init__(self):
        self.matrix = []
        self.master = Tk()
        self.master.title("A*")
        self.grid_size = 10
        self.square_size = 48

        self.predator_position = None
        self.prey_position = None
        self.current_position_predator = self.predator_position
        self.current_position_prey = self.prey_position

        self.current_state = "wall"
        self.current_player = "predator" # Values: predator ou prey

        self.__pre_fill_matrix()

        self.max_num_square_predator_walk = 2
        self.max_num_square_prey_walk = 1

        # self.__update()

        self.canvas = Canvas(self.master, width=900, height=550)
        self.canvas.bind("<Button-1>", self.__set_positions)
        self.canvas.pack()

        self.background_image = Image.open("../imagens/pacman_background.jpg")
        self.background_image = self.background_image.resize((900, 550))
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)

        self.predator_image_path = "../imagens/pacman.png"
        self.start_image = Image.open(self.predator_image_path)
        self.start_photo = ImageTk.PhotoImage(self.start_image)

        self.prey_image_path = "../imagens/dot.png"
        self.goal_image = Image.open(self.prey_image_path)
        self.goal_photo = ImageTk.PhotoImage(self.goal_image)

        self.state_button = None

        # self.open_list = PriorityQueue()
        self.visited_list = set()

        # self.start_image_id = self.canvas.create_image(
        #     self.predator_position[1] * self.square_size + self.square_size / 2,
        #     self.predator_position[0] * self.square_size + self.square_size / 2,
        #     image=self.start_photo,
        #     tags="grid"
        # )

        # self.goal_image_id = self.canvas.create_image(
        #     self.prey_position[1] * self.square_size + self.square_size / 2,
        #     self.prey_position[0] * self.square_size + self.square_size / 2,
        #     image=self.goal_photo,
        #     tags="grid"
        # )

        # self.grid_lines()

        # self.master.after(1000, self.loop)
        self.__update()

    def __pre_fill_matrix(self): # criação de matriz de objetos Square.
        for x in range(self.grid_size): #loop para percorrer o labirinto
            self.matrix.append([])# criação das linhas do labirinto.
            for y in range(self.grid_size):
                self.matrix[x].append(Square(x=x, y=y)) # criação de um novo quadrado  

    def draw_interface(self):
        self.master.mainloop()
    
    def __get_square(self, row, col):
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            if self.matrix[row][col]:
                return self.matrix[row][col]

    def __set_positions(self, event):
        row = event.y // self.square_size
        col = event.x // self.square_size

        print('position', row, col)
        print(self.current_state)

        current_square: Square = self.__get_square(row, col)

        if self.current_state == "wall":
            current_square.state = "wall"
        elif self.current_state == "predator":
            if self.predator_position is None:
                current_square.state = "predator"
                self.predator_position = (row, col)
        elif self.current_state == "prey":
            if self.prey_position is None:
                current_square.state = "prey"
                self.prey_position = (row, col)

        self.__update()

    def __set_predator(self):
        self.current_state = "predator"

    def __set_prey(self):
        self.current_state = "prey"

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

    def __update(self,):
        self.canvas.delete("grid")

        if self.state_button:
            self.state_button.destroy()
        
        # Dicionário para armazenar as referências às imagens
        self.image_references = {}

        self.grid_lines()

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                square: Square = self.__get_square(x, y)
                state = square.state
                print(state)
                if state == "predator":
                    image_path = self.predator_image_path
                elif state == "prey":
                    image_path = self.prey_image_path
                    print(image_path)
                else:
                    image_path = None

                if image_path:
                    if image_path not in self.image_references:
                        img = Image.open(image_path)
                        photo_img = ImageTk.PhotoImage(img)
                        self.image_references[image_path] = photo_img
                    else:
                        photo_img = self.image_references[image_path]

                    self.canvas.create_image(
                        y * self.square_size + self.square_size / 2,
                        x * self.square_size + self.square_size / 2,
                        image=photo_img,
                        tags="grid"
                    )
                elif state:
                    color = {
                        "": "",
                        "wall": "#000000",
                        "path": "#8e6c40",
                        "visited": "#12907A",
                        # "prey": "pink"
                    }.get(state, "")

                    self.canvas.create_rectangle(
                       ( y * self.square_size),
                        (x * self.square_size),
                        (y + 1) * self.square_size,
                        (x + 1) * self.square_size,
                        fill=color,
                        # outline="black",
                        tags="grid"
                    )

        if self.current_state == "wall":
            self.state_button = Button(
                self.master, text="Selecione a posição da presa", command=self.__set_prey)
            self.state_button.pack()
        elif self.current_state == "prey":
            self.state_button = Button(
                self.master, text="Selecione a posição do predador", command=self.__set_predator)
            self.state_button.pack()
        elif self.current_state == "predator":
            self.state_button = Button(
                self.master, text="Iniciar algoritmo", command=self.__start_algorithm)
            self.state_button.pack()

    def __start_algorithm(self):
        pass

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

    def __execute_algorithm(self, start, goal):
        open_list = set()
        visited_list = set()

        start_square = self.__get_square(start[0], start[1])
        goal_square = self.__get_square(goal[0], goal[1])

        start_square.g = 0
        start_square.g = self.__heuristic(start_square)
        start_square.f - start_square.g + start_square.h

        open_list.add_element(start, start_square.f)

        while open_list:
            # self.__update()
            time.sleep(0.2)

            if self.current_player == "predator":
                current_square = self.__find_min_f(open_list)
                new_start = (current_square.x, current_square.y)
            else:
                current_square = self.__find_max_f(open_list)
                new_goal = (current_square.x, current_square.y)
            
            if current_square == goal:
                return True
            
            open_list.remove(current_square)
            visited_list.add(current_square)

            # Lógica de econtrar os vizinhos


            # Thread talvez tenha que ficar aqui


    def __find_min_f(self, open_list):
        min_f_square = None
        min_f_value = float('inf')

        for square_position in open_list:
            square: Square = self.__get_square(square_position[0], square_position[1])
            if square.f < min_f_value:
                min_f_square = square
                min_f_value = square.f

        # Retorna um objeto do tipo square
        return min_f_square
    
    def __find_max_f(self, open_list):
        max_f_square = None
        max_f_value = -1

        for square_position in open_list:
            square: Square = self.__get_square(square_position[0], square_position[1])

            if square.f > max_f_value:
                max_f_square = square
                max_f_value = square.f

        # Retorna um objeto do tipo square
        return max_f_square
    
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
        self.prey_position = (
            (self.prey_position[0] + 1) % self.grid_size,
            self.prey_position[1]
        )

    def __run_a_star(self):
        self.__update()

        def a_star_thread():
            path_found = None
            if path_found:
                print("Presa foi encontrada")
            else:
                self.__update()
                print("Presa não encontrada")

        thread = threading.Thread(target=a_star_thread)
        thread.start()
        self.player = "predator"

    def loop(self):
        self.update_positions()

        # Draw Pac-Man and goal based on updated positions
        self.pacman(self.current_position)
        self.goal(self.prey_position)

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