import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.states.menu_state import MenuState

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MenuState(self)

    def change_state(self, new_state):
        self.state = new_state

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else: 
                    self.state.handle_event(event)
            
            self.state.update(dt)
            self.state.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
        sys.exit()