from tkinter import *
from square import Square
from priority_queue import PriorityQueue
from PIL import Image, ImageTk

class Interface:
    def __init__(self, matrix=None):
        self.matrix = []
        self.master = Tk()
        self.master.title("A*")
        self.square_dimension = 48
        self.size = 10
        self.current_state = "wall"
        self.__pre_fill_matrix()

        self.canvas = Canvas(self.master, width=900, height=550)
        self.canvas.bind("<Button-1>", self.__set_square_color)
        self.canvas.pack()
        # Carregando uma imagem de fundo
        self.background_image = Image.open("imagens/banner.jpg")
        self.background_image = self.background_image.resize((900, 550))  # Redimensiona a imagem
        self.background_photo = ImageTk.PhotoImage(self.background_image)
       
        # Adicionando a imagem de fundo ao Canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.background_photo)
       

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
        
        # Dicionário para armazenar as referências às imagens
        self.image_references = {}

        for y in range(self.size):
            for x in range(self.size):
                square: Square = self.__get_square(x, y)
                state = square.state

                if state == "start":
                    image_path = "imagens/robo.png"
                elif state == "goal":
                    image_path = "imagens/caixa.png"
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
                        y * self.square_dimension + self.square_dimension / 2,
                        x * self.square_dimension + self.square_dimension / 2,
                        image=photo_img,
                        tags="grid"
                    )
                else:
                    color = {
                        "": "",
                        "wall": "#000000",
                        "path": "#8e6c40",
                        "visited": "#12907A"
                    }.get(state, "")

                    margin = 5
                    self.canvas.create_rectangle(
                       ( y * self.square_dimension) + margin,
                        (x * self.square_dimension) + margin,
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
            current_position = self.open_list.delete_min()
            x, y = current_position
            current_square: Square = self.matrix[y][x]

            self.visited_list.add(current_position) #marcação do no visitado.

            current_square.visited = True
            if current_position != self.start_position:
                current_square.state = "visited"
        
            self.__update()

            if current_position == self.goal_position:
                self.__reconstruct_path(current_square)
                return

            neighbors_positions = self.__find_neighbors(current_position) #vizinhos validos.

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

    def __reconstruct_path(self, current_square):
        while current_square.parent:
            current_square.state = "path"
            current_square = current_square.parent
        self.__update()


if __name__ == "__main__":
    size = 10
    interface = Interface()
    interface.draw_interface()
