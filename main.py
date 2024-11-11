import sys
import time
import pygame
from enum import Enum

class BoardSymbols(Enum):
    BOARD = 'B'
    SNAKE = 'S'
    FOOD  = 'F'

class Simulation():
    def __init__(self):
        self.running = True
        self.display_surf = None
        self.size = self.width, self.height = 640, 400

    def on_init(self):
        pygame.init()
        self.display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def on_loop(self):
        pass

    def on_render(self):
        pass

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        if self.on_init() == False:
            self.running = False
 
        while( self.running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

        self.on_cleanup()

class Snake():
    def __init__(self):
        self.coordinates = [[0,0]]

class Game():
    def __init__(self, board_size=50, fps=1):
        self.running = True
        self.screen = None
        self.size = self.width, self.height = 640, 400
        self.board_size = board_size
        self.padding_h = 100
        self.board_h = self.height - self.padding_h
        self.fps = fps  # Target frames per second
        self.clock = pygame.time.Clock()  # Pygame clock to control FPS

    def on_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.running = True
        
        self.board = [[BoardSymbols.BOARD.value for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.square_width = self.board_h / self.board_size

        self.square_surface = pygame.Surface((self.square_width, self.square_width))
        self.square_surface.fill('red')

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def on_loop(self):
        pygame.display.set_caption(str(time.time()))

    def on_render(self):
        total_board_height = (self.board_size * self.square_width) + (self.board_size - 1)
        start_y = (self.height / 2) - (total_board_height / 2)

        total_board_width = (self.board_size * self.square_width) + (self.board_size - 1)
        start_x = (self.width / 2) - (total_board_width / 2)

        for row in self.board:
            x_pos = start_x
            for cell in row:
                self.screen.blit(self.square_surface, (x_pos, start_y))
                x_pos += self.square_width + 1
            start_y += self.square_width + 1

        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        self.on_init()
        while self.running:
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()

            self.clock.tick(self.fps)

        self.on_cleanup()

if __name__ == "__main__":
    game = Game(fps=5)
    game.run()