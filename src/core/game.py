import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from src.states.menu_state import MenuState
from src.core.audio_manager import AudioManager

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = AudioManager()
        self.state = MenuState(self)

        # Sons
        self.audio.load_sound("menu_theme", "assets/sounds/ChicoBentoSimulator.mp3", 0.8)
        self.audio.load_sound("menu_select", "assets/sounds/MenuSelectionClick.wav", 0.6)
        self.audio.load_sound("pause_menu", "assets/sounds/pause.mp3", 0.6)
        self.audio.load_sound("steps", "assets/sounds/steps.flac", 0.3)
        self.audio.load_sound("planting", "assets/sounds/plantar.flac", 0.6)
        self.audio.load_sound("harvest", "assets/sounds/colher.flac", 0.6)
        self.audio.load_sound("money", "assets/sounds/money.ogg", 0.6)

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