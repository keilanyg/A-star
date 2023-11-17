from tkinter import *
from node import Node
from priority_queue import PriorityQueue
from PIL import Image, ImageTk

def generate_matrix(size: int):
    import numpy as np
    matrix = np.full((size, size), 1)
    print(matrix)
    return matrix


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

    def __pre_fill_matrix(self): # criação de matriz de objetos Node.
        for y in range(self.size): #loop para percorrer o labirinto
            self.matrix.append([])# criação das linhas do labirinto.
            for x in range(self.size):
                self.matrix[y].append(Node(x=x, y=y)) # criação de um novo nó  

    def __get_node(self, x, y):
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
        
        # Dicionário para armazenar as referências às imagens
        self.image_references = {}

        for y in range(self.size):
            for x in range(self.size):
                node: Node = self.__get_node(x, y)
                state = node.state

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
            current_node_position = self.open_list.delete_element()
            x, y = current_node_position
            current_node: Node = self.matrix[y][x]

            self.visited_list.add(current_node_position) #marcação do no visitado.

            current_node.visited = True
            if current_node_position != self.start_position:
                current_node.state = "visited"
        
            self.__update()

            if current_node_position == self.goal_position:
                self.__reconstruct_path(current_node)
                return

            neighbors_positions = self.__find_neighbors(current_node_position) #vizinhos validos.

            for neighbor in neighbors_positions: # loop para ignorar os vizinhos visitados.
                if neighbor in self.visited_list:# ignora o vizinho visitado.
                    continue

                neighbor_node = self.__get_node(neighbor[0], neighbor[1]) # obtendo o nó do vizinho.

                if neighbor_node.state == "wall":
                    continue  # Ignore obstáculos
                
                # Calcula o novo custo g para chegar ao vizinho a partir do nó atual.
                g_score = current_node.g + \
                    self.__calculate_g_score(current_node, neighbor_node)
                print('position', (neighbor[0], neighbor[1]))
                print('valores g:', neighbor_node.g, 'h:', neighbor_node.h, 'f:', neighbor_node.f)

                # Se o novo custo g é menor do que o custo g anterior do vizinho
                if g_score < neighbor_node.g:
                    neighbor_node.parent = current_node
                    neighbor_node.g = g_score
                    neighbor_node.h = self.__heuristic(neighbor)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    self.open_list.add_element(neighbor, neighbor_node.f)
                print('valores atualizados g:', neighbor_node.g, 'h:', neighbor_node.h, 'f:', neighbor_node.f)

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
