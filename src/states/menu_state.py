import pygame
from src.states.base_state import BaseState
from settings import DARK_GREEN, WHITE, YELLOW, MENU_BG

class MenuState(BaseState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 36)
        self.options = ["Novo Jogo", "Carregar Jogo", "Controles", "Sair"]
        self.selected = 0
        self.background = pygame.image.load(MENU_BG).convert()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected -1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        for i, option in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            text = self.font.render(option, True, color)
            screen.blit(text, (100, 120 + i * 50))