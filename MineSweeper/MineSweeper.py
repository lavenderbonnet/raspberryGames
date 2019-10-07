import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.signal import convolve2d
import sys
import pygame

class Grid:
    def __init__(self, N, n_mines):
        self.N = N
        self.n_mines = n_mines
        ps = [1-(n_mines/N**2), n_mines/N**2]
        self.grid = np.random.choice([0, -1], size=(N, N), p=ps)
        self.init_grid()
        self.selection_grid = np.ones((N, N)) * 10

    def full_reset(self, N=15, n_mines=20):
        self.N = N
        self.n_mines = n_mines
        ps = [1-(n_mines/N**2), n_mines/N**2]
        self.grid = np.random.choice([0, -1], size=(N, N), p=ps)
        self.init_grid()
        self.selection_grid = np.ones((N, N)) * 10

    def init_grid(self):
        nn = np.array([[-1, -1, -1],
                       [-1,  0, -1],
                       [-1, -1, -1]])
        grid = convolve2d(self.grid, nn, mode='same', boundary='fill')
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == -1:
                    grid[i][j] = -1
        self.grid = grid.copy()

    def _show_grid(self):
        plt.imshow(self.grid)
        plt.colorbar()
        plt.show()

    def cell_clicked(self, i, j):
        # val = self.grid[i][j]
        if self.grid[i][j] == -1:
            # bomb hit
            # self.selection_grid[i][j] = -2
            self.bomb_hit(i, j)
            return 1
        elif self.grid[i][j] == 0:
            # No bombs
            zeros = True # unused
            x = i
            y = j
            self.selection_grid[i][j] = 0
            self.reveal_empty_neighbours(i, j)
        else:
            self.selection_grid[i][j] = self.grid[i][j]
        return 0

    def reveal_empty_neighbours(self, i, j):
        for x in range(i -1, i + 2):
            for y in range(j - 1, j + 2):
                if x < 0 or x >= self.N or y < 0 or y >= self.N or (x == i and y == j):
                    continue
                if self.grid[x][y] == 0 and self.selection_grid[x][y] != 0:
                    self.selection_grid[x][y] = self.grid[x][y]
                    self.reveal_empty_neighbours(x, y)
                else:
                    self.selection_grid[x][y] = self.grid[x][y]
                

    def flag_added(self, i, j):
        # print("Flag added: %d, %d" % (i, j))
        # Flag values set to 9 as this is greatr than all possible values.
        # (in a 2d grid).
        if self.selection_grid[i][j] == 10:
            # If cell is empty add a flag
            self.selection_grid[i][j] = 9
        elif self.selection_grid[i][j] == 9:
            # If already flagged.
            self.selection_grid[i][j] = 10
            # Set back to original unflaged value of 10.

    def bomb_hit(self, i, j):
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == -1:
                    self.selection_grid[i][j] = -1
        # self._show_grid()

    def reset(self):
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == -1:
                    self.selection_grid[i][j] = 10

    def check_complete(self):
        for i in range(self.N):
            for j in range(self.N):
                if self.grid[i][j] == -1 and self.selection_grid[i][j] != 9:
                    return 0
        return 1

    def select_point(self):
        """ Not used """
        a = input("Enter the grid location:").split(" ")
        a = list(map(int, a))
        self.cell_clicked(a[0], a[1])

class Game:
    def __init__(self, grid):
        self.grid = grid
        pygame.init()
        self.width = 900
        self.win = pygame.display.set_mode((self.width, self.width))
        pygame.display.set_caption("MineSweeper")
        self.flag = pygame.image.load("red_flag.png") # Still haveing issues
        self.complete()
        self.run_game() ## Needs removed once a ome page has been made
        # self.win.blit(self.flag, (0,0))

    def get_grid_pos(self, mx, my):
        """ Takes the mouse position in pixels and translates in to grid position. """
        n_boxes = self.grid.N
        buffer = 5
        box_width = (self.width-buffer/2) // n_boxes
        grid_x = int(mx // box_width)
        grid_y = int(my // box_width)
        # print(grid_x, grid_y)
        return grid_x, grid_y

    def run_game(self):
        running = True
        clock = pygame.time.Clock()
        fps = 30
        while running:
            clock.tick(fps)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            keys = pygame.key.get_pressed()
            click1, click2, click3 = pygame.mouse.get_pressed()
            if click1:
                fps = 5
                mx, my = pygame.mouse.get_pos()
                grid_x, grid_y = self.get_grid_pos(mx, my)
                if(self.grid.cell_clicked(grid_x, grid_y)):
                    if not self.end_game():
                        running = False
            elif click3:
                fps = 5
                mx, my = pygame.mouse.get_pos()
                grid_x, grid_y = self.get_grid_pos(mx, my)
                self.grid.flag_added(grid_x, grid_y)
            else:
                fps = 30
            if keys[pygame.K_r]:
                self.grid.reset()
            self.draw_grid()
            pygame.display.update()
            if self.grid.check_complete():
                self.complete()


    def draw_grid(self):
        n_boxes = self.grid.N
        buffer = 3
        box_width = (self.width-buffer/2) // n_boxes
        font = pygame.font.Font('freesansbold.ttf', 30)
        for i in range(n_boxes):
            for j in range(n_boxes):
                # print(self.grid.selection_grid[i][j])
                val = str(int(self.grid.selection_grid[i][j]))
                if val == "10" or val == "0":
                    val = ""
                if val == "-1":
                    val = "!"
                if val == "9":
                    val = "/>"
                box_col = (170, 170, 170)
                col = (0, 0, 0)
                if self.grid.selection_grid[i][j] == 10: # or self.grid.selection_grid[i][j] == 9:
                    box_col = (200, 200, 200)
                elif self.grid.selection_grid[i][j] == 0:
                    box_col = (113, 196, 71)
                elif self.grid.selection_grid[i][j] == 1:
                    col = (20, 150, 0)
                elif self.grid.selection_grid[i][j] == 2:
                    col = (40, 120, 0)
                elif self.grid.selection_grid[i][j] == 3:
                    col = (60, 100, 0)
                elif self.grid.selection_grid[i][j] == 4:
                    col = (80, 80, 0)
                elif self.grid.selection_grid[i][j] == 5:
                    col = (100, 60, 0)
                elif self.grid.selection_grid[i][j] == 6:
                    col = (120, 40, 0)
                elif self.grid.selection_grid[i][j] == 7:
                    col = (140, 20, 0)
                elif self.grid.selection_grid[i][j] == 8:
                    col = (150, 0, 0)
                elif self.grid.selection_grid[i][j] == 9:
                    box_col = (0, 50, 255)
                elif self.grid.selection_grid[i][j] == -1:
                    box_col = (200, 0, 0)
                
                pygame.draw.rect(self.win, box_col, ((i * box_width) + buffer, (j * box_width) + buffer, box_width - buffer, box_width - buffer))
                text = font.render("%s" % val, True, col)
                textRect = text.get_rect()
                textRect.center = ((i * box_width) + buffer + box_width // 2, (j * box_width) + buffer + box_width // 2)
                
                self.win.blit(text, textRect)
                # self.win.blit(self.flag, (0,0))
    
    def end_game(self):
        self.draw_grid()
        pygame.display.update()
        print("GAME OVER")
        pygame.time.delay(1000)

        font = pygame.font.Font('freesansbold.ttf', 32) 
        go_text = font.render("GAME OVER!", True, (0, 0, 0))
        cont_text = font.render("Press space bar to continue.", True, (0, 0, 0))
        go_textRect = go_text.get_rect()  
        cont_textRect = cont_text.get_rect()
        go_textRect.center = (self.width // 2, self.width // 2) 
        cont_textRect.center = (self.width // 2, 6.5 * self.width// 8)
        self.win.blit(go_text, go_textRect)
        self.win.blit(cont_text, cont_textRect)

        pygame.display.update()

        pygame.time.delay(1500)
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    waiting = False
                    self.win.fill(0)
                    # self.grid.full_reset()
                    self.complete()
                    return 1
        return 0

    def complete(self):
        self.draw_grid()
        pygame.time.delay(1500)
        self.win.fill((50, 115,220, 0.3))
        waiting = True

        positions = [] ## fill with button positions
        pygame.draw.rect(self.win, (170, 255, 195), (0.05 * self.width, 0.75 * self.width, 0.26 * self.width, 0.1 * self.width))
        pygame.draw.rect(self.win, (255, 225, 25), (0.36 * self.width, 0.75 * self.width, 0.26 * self.width, 0.1 * self.width))
        pygame.draw.rect(self.win, (230, 25, 75), (0.67 * self.width, 0.75 * self.width, 0.26 * self.width, 0.1 * self.width))
        positions.append(ButtonPosition(0.05 * self.width, 0.75 * self.width, 0.26 * self.width, 0.1 * self.width))
        positions.append(ButtonPosition(0.36 * self.width, 0.75 * self.width, 0.26 * self.width, 0.1 * self.width))
        positions.append(ButtonPosition(0.67 * self.width, 0.75 * self.width, 0.26 * self.width, 0.1 * self.width))

        font = pygame.font.Font('freesansbold.ttf', 64) 
        main_text = font.render("MineSweeper", True, (0, 0, 0))

        font = pygame.font.Font('freesansbold.ttf', 32) 
        easy_text = font.render("Easy", True, (0, 0, 0))
        medium_text = font.render("Medium", True, (0, 0, 0))
        hard_text = font.render("Hard", True, (0, 0, 0))

        main_textRect = main_text.get_rect()  
        easy_textRect = easy_text.get_rect()  
        medium_textRect = medium_text.get_rect()
        hard_textRect = hard_text.get_rect()

        main_textRect.center = (self.width * 0.5, self.width * 0.3) 
        easy_textRect.center = (self.width * 0.18, self.width * 0.8) 
        medium_textRect.center = (self.width * 0.49, self.width * 0.8)
        hard_textRect.center = (self.width * 0.80, self.width * 0.8)

        self.win.blit(main_text, main_textRect)
        self.win.blit(easy_text, easy_textRect)
        self.win.blit(medium_text, medium_textRect)
        self.win.blit(hard_text, hard_textRect)

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            keys = pygame.key.get_pressed()
            click1, click2, click3 = pygame.mouse.get_pressed()
            if click1:
                mx, my = pygame.mouse.get_pos()
                if self.button_pressed(positions, mx, my) == 1:
                    self.grid.full_reset(9, 10)
                    self.win.fill(0)
                    pygame.time.delay(1500)
                    return 1
                elif self.button_pressed(positions, mx, my) == 2:
                    self.grid.full_reset(15, 40)
                    self.win.fill(0)
                    pygame.time.delay(1500)
                    return 1
                elif self.button_pressed(positions, mx, my) == 3:
                    self.grid.full_reset(20, 100)
                    self.win.fill(0)
                    pygame.time.delay(1500)
                    return 1
            pygame.display.update()
        return 0


    def button_pressed(self, positions, mx, my):
        for i, button in enumerate(positions):
            if mx > button.x and mx < button.w + button.x:
                if my > button.y and my < button.y + button.h:
                    return i + 1
        return 0

class ButtonPosition:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.w = width
        self.h = height


def main(argv):
    argv = [15, 68]
    if len(argv) != 2:
        print("python MineSweeper.py N n_mines")
        sys.exit()
    grid = Grid(int(argv[0]), int(argv[1]))
    game = Game(grid)
    

if __name__ == '__main__':
    main(sys.argv[1:])
