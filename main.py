import pygame

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


class Game():
    def __init__(self):
        self.running = True
        self.screen  = None
        self.size    = self.width, self.height = 640, 400

    def on_init(self):
        pygame.init()
        self.screen  = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

    def on_loop(self):
        pass

    def on_render(self):
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def run(self):
        self.on_init()

        while( self.running):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()

        self.on_cleanup()


if __name__ == "__main__":
    game = Game()
    game.run()