from tkinter import *
from PIL import Image, ImageTk
from square import Square
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
        self.current_position_predator = None
        self.current_position_prey = None

        self.current_state = "wall"
        self.current_player = "predator"  # Values: predator ou prey

        self.__pre_fill_matrix()

        self.max_num_square_predator_walk = 2
        self.max_num_square_prey_walk = 1
        self.num_square_walk = 0

        # self.__update()

        self.canvas = Canvas(self.master, width=900, height=550)
        self.canvas.bind("<Button-1>", self.__set_positions)
        self.canvas.pack()

        self.start_image_id = None
        self.goal_image_id = None

        self.background_image = Image.open("../imagens/pacman_background.jpg")
        self.background_image = self.background_image.resize((900, 550))
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        self.canvas.create_image(
            0, 0, anchor="nw", image=self.background_photo)

        self.predator_image_path = "../imagens/pacman.png"
        self.start_image = Image.open(self.predator_image_path)
        self.start_photo = ImageTk.PhotoImage(self.start_image)

        self.prey_image_path = "../imagens/dot.png"
        self.goal_image = Image.open(self.prey_image_path)
        self.goal_photo = ImageTk.PhotoImage(self.goal_image)

        self.state_button = None

        self.open_set_predator = set()
        self.open_set_prey = set()

        self.visited_list_predator = set()
        self.visited_list_prey = set()

        self.after_id = None  # ID do agendador do Tkinter

        self.count = 0

        self.__update()

    def __pre_fill_matrix(self):  # criação de matriz de objetos Square.
        for x in range(self.grid_size):  # loop para percorrer o labirinto
            self.matrix.append([])  # criação das linhas do labirinto.
            for y in range(self.grid_size):
                # criação de um novo quadrado
                self.matrix[x].append(Square(x=x, y=y))

    def draw_interface(self):
        self.master.mainloop()

    def __get_square(self, row, col):
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return self.matrix[row][col] if self.matrix[row][col] else None
        else:
            print(f"Fora do gráfico: ({row}, {col})")
            return None

    def __set_positions(self, event):
        row = event.y // self.square_size
        col = event.x // self.square_size

        # print('position', row, col)
        print(self.current_state)

        current_square: Square = self.__get_square(row, col)

        if self.current_state == "wall":
            current_square.state = "wall"
        elif self.current_state == "predator":
            if self.current_position_predator is None:
                current_square.state = "predator"
                self.current_position_predator = (row, col)
        elif self.current_state == "prey":
            if self.current_position_prey is None:
                current_square.state = "prey"
                self.current_position_prey = (row, col)

        self.__update()

    def __set_predator(self):
        self.current_state = "predator"

    def __set_prey(self):
        self.current_state = "prey"

    def pacman(self, position):
        if self.start_image_id:
            self.canvas.delete(self.start_image_id)

        self.start_image_id = self.canvas.create_image(
            position[1] * self.square_size + self.square_size / 2,
            position[0] * self.square_size + self.square_size / 2,
            image=self.start_photo,
            tags="grid"
        )

    def goal(self, position):
        if self.goal_image_id:
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
                        (y * self.square_size),
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
                self.master, text="Iniciar algoritmo", command=self.update_interface)
            self.state_button.pack()

    def __heuristic(self, current, goal):
        x1, y1 = current
        x2, y2 = goal
        return abs(x1 - x2) + abs(y1 - y2)

    def __calculate_g_score(self, current_square, neighbor_square):
        dx = abs(current_square.x - neighbor_square.x)
        dy = abs(current_square.y - neighbor_square.y)
        if dx == 1 and dy == 1:
            return 14
        else:
            return 10
        
    def reset_square_values(self, ):
        for row in self.matrix:
            for square in row:
                square.g = float("inf")
                square.h = 0
                square.f = 0

    def __find_path(self, start: tuple, goal: tuple, open_list: set = set(), visited_list: set = set(), player=None):
        start_square = self.__get_square(start[0], start[1])
        goal_square = self.__get_square(goal[0], goal[1])

        start_square.g = 0
        start_square.h = self.__heuristic(start, goal)
        start_square.f = start_square.g + start_square.h

        open_list.add(start_square)

        # Falta alternar os valores pra cada player e alterar os valores e cada vez que eles se encontram
        while open_list:
            time.sleep(0.2)

            current_square = self.__find_min_f(open_list)
            current_position = (current_square.x, current_square.y)

            # print('posição atual:', current_position, self.current_player)

            # if self.current_position_predator == self.current_position_prey:
            #     print("encontrou")
            #     self.master.after(200, self.__find_path)

            if current_position == goal:
                path = self.__reconstruct_path(goal)
                self.num_square_walk += 1
                
                print('caminho a ser percorrido:', path)
                if self.current_player == "predator":
                    print("posição antiga", self.current_position_predator)
                    print("posição a ser acessada", path[-2])
                    self.current_position_predator = path[-2]

                    self.reset_square_values()

                    if self.current_position_predator != self.current_position_prey:
                        # print("ainda n achou")
                        self.current_position_predator = path[-3]
                        # for i in range(self.max_num_square_predator_walk, 2, -1):
                        #     pass
                        print("posição a ser acessada 2", path[-3])
                return True

            open_list.remove(current_square)
            visited_list.add(current_square)

            neighbors_squares = self.__find_neighbors(current_position)

            # if self.current_player == "prey":
            #     print('vizinhos da presa', neighbors_squares)

            for neighbor in neighbors_squares:
                if neighbor in visited_list or neighbor.state == "wall":
                    continue

                g_score = current_square.g + self.__calculate_g_score(
                    current_square, neighbor
                )

                if g_score < neighbor.g:
                    neighbor.parent = current_square
                    neighbor.g = g_score
                    neighbor.h = self.__heuristic(
                        (neighbor.x, neighbor.y), goal)
                    neighbor.f = neighbor.g + neighbor.h
                    open_list.add(neighbor)

    def walk_prey(self, current_position: tuple, goal: tuple):
        current_square = self.__get_square(current_position[0], current_position[1])
        neighbors_squares = self.__find_neighbors(current_position)

        for neighbor in neighbors_squares:
            if neighbor.state == "wall":
                continue

            g_score = current_square.g + self.__calculate_g_score(
                current_square, neighbor
            )

            if g_score < neighbor.g:
                neighbor.parent = current_square
                neighbor.g = g_score
                neighbor.h = self.__heuristic((neighbor.x, neighbor.y), goal)
                neighbor.f = neighbor.g + neighbor.h

        max_f_square = max(neighbors_squares, key=lambda square: square.f)
        self.current_position_prey = (max_f_square.x, max_f_square.y)
        self.num_square_walk += 1
        print("nova posição presa", self.current_position_prey)
        self.reset_square_values()
        return max_f_square

    def update_interface(self):
        """ Pegar as casas de pesquisa de acordo com o melhor caminho encontrado, acho que precisa percorrer toda vez que muda a posição """
        while self.current_position_predator != self.current_position_prey:
            if self.current_player == "predator" and self.num_square_walk >= 1:
                print("entrou aqui")
                self.current_player = "prey"
                self.num_square_walk = 0
            elif self.current_player == "prey" and self.num_square_walk >= self.max_num_square_prey_walk:
                print("agora entrou aqui")
                self.current_player = "predator"
                self.num_square_walk = 0

            print("player", self.current_player)
            print('posição atual predador', self.current_position_predator)
            print('posição atual presa', self.current_position_prey)
            self.call_search_logic()
            # self.master.after(200, self.call_search_logic)
        else:
            print("encontrou o caminho")
            return True

    def call_search_logic(self):
        # and self.num_square_walk < self.max_num_square_predator_walk:
        if self.current_player == "predator":
            return self.__find_path(self.current_position_predator, self.current_position_prey, set(), set())
        # and self.num_square_walk < self.max_num_square_prey_walk:
        elif self.current_player == "prey":
            # self.__find_path(self.current_position_prey, self.current_position_predator)
            return self.walk_prey(self.current_position_prey, self.current_position_predator)

        # self.__update()

    def __find_min_f(self, open_list):
        min_f_square = min(open_list, key=lambda square: square.f)
        return min_f_square

    def __find_neighbors(self, current):
        x, y = current
        neighbors = []

        for n_x in [-1, 0, 1]:
            for n_y in [-1, 0, 1]:
                if n_x == 0 and n_y == 0:
                    continue

                new_x, new_y = x + n_x, y + n_y
                cur_neighbor_square = self.__get_square(new_x, new_y)

                if cur_neighbor_square and cur_neighbor_square.state != "wall":
                    neighbors.append(cur_neighbor_square)

        return neighbors

    def update_positions(self):
        """ Update Pac-Man and goal positions based on the A* algorithm results """
        if self.current_position_predator and self.current_position_prey:
            # Update Pac-Man position
            self.current_position_predator = (
                (self.current_position_predator[0] + 2) % self.grid_size,
                self.current_position_predator[1]
            )

            # Update goal position
            self.current_position_prey = (
                (self.current_position_prey[0] + 1) % self.grid_size,
                self.current_position_prey[1]
            )

    def loop(self):
        self.update_positions()

        if self.current_position_predator and self.current_position_prey:
            # Draw Pac-Man and goal based on updated positions
            self.pacman(self.current_position_predator)
            self.goal(self.current_position_prey)

            self.master.after(1000, self.loop)

    def grid_lines(self):
        for i in range(1, self.grid_size):
            x = i * self.square_size
            self.canvas.create_line(
                x, 0, x, self.square_size * self.grid_size, fill="black", tags="grid")
            y = i * self.square_size
            self.canvas.create_line(
                0, y, self.square_size * self.grid_size, y, fill="black", tags="grid")

    def __reconstruct_path(self, goal: tuple):
        path = []
        current_square = self.__get_square(goal[0], goal[1])

        while current_square:
            path.append((current_square.x, current_square.y))
            current_square = current_square.parent

        # path.reverse()
        return path


if __name__ == "__main__":
    interface = Interface()
    # interface.loop()
    """ o método loop só pode ser iniciado após as posições serem definidas"""
    interface.draw_interface()
