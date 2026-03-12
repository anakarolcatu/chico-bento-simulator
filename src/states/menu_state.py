import pygame
from src.states.base_state import BaseState
from src.ui.buttons import Button
from src.utils.spritesheet import get_sprite
from src.utils.ui_helper import nine_slice
from settings import BLACK, BROWN, MENU_BG, SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.font_manager import FontManager

class MenuState(BaseState):
    def __init__(self, game):
        super().__init__(game)

        self.font = FontManager.get(13)
        self.title_font = FontManager.get(32)
        self.title_text = "CHICO BENTO SIMULATOR"

        # Imagem de fundo 
        img = pygame.image.load(MENU_BG).convert()
        img_ratio = img.get_width() / img.get_height()
        screen_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
        if img_ratio > screen_ratio:
            new_width = int(img_ratio * SCREEN_HEIGHT)
            self.background = pygame.transform.scale(img, (new_width, SCREEN_HEIGHT))
        else:
            new_height = int(SCREEN_WIDTH / img_ratio)
            self.background = pygame.transform.scale(img, (SCREEN_WIDTH, new_height))
        self.bg_rect = self.background.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Fundo do menu
        self.menu_sheet = pygame.image.load("assets/ui/Main_tiles.png").convert_alpha()

        panel_base = get_sprite(self.menu_sheet, 207, 196, 49, 40)
        self.panel = nine_slice(panel_base, 260, 360, 4)
        self.panel_rect = self.panel.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Botões do menu
        self.button_sheet = pygame.image.load("assets/ui/Buttons.png").convert_alpha()
        normal_button = get_sprite(self.button_sheet, 104, 130, 32, 15)
        selected_button = get_sprite(self.button_sheet, 8,130, 32, 15)
        pressed_button = get_sprite(self.button_sheet, 56, 130, 32, 15)
        
        normal_button = pygame.transform.scale(normal_button, (210, 60))
        selected_button = pygame.transform.scale(selected_button, (210, 60))
        pressed_button = pygame.transform.scale(pressed_button, (210, 60))

        center_x = SCREEN_WIDTH // 2
        start_y = 250
        gap = 65
        self.options = ["NOVO JOGO", "CARREGAR JOGO", "CONTROLES", "SAIR"]

        self.buttons = [
            Button(normal_button, selected_button, pressed_button, center_x, start_y + 0 * gap, self.options[0], self.font, BLACK, BROWN),
            Button(normal_button, selected_button, pressed_button, center_x, start_y + 1 * gap, self.options[1], self.font, BLACK, BROWN),
            Button(normal_button, selected_button, pressed_button, center_x, start_y + 2 * gap, self.options[2], self.font, BLACK, BROWN),
            Button(normal_button, selected_button, pressed_button, center_x, start_y + 3 * gap, self.options[3], self.font, BLACK, BROWN),
        ]
        self.selected = 0
        self.update_selection()

    def update_selection(self):
        for i, button in enumerate(self.buttons):
            if i == self.selected:
                button.set_state("selected")
            else:
                button.set_state("normal")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected -1) % len(self.options)
                self.update_selection()
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self.update_selection()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.activate_selected()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected = i
                    self.update_selection()
                    self.activate_selected()

    def activate_selected(self):
        option = self.selected
        if option == 0:
            print("Iniciar novo jogo")
        elif option == 1:
            print("Carregar jogo")
        elif option == 2:
            print("Exibir controles")
        elif option == 3:
            self.game.running = False

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.selected = i
                self.update_selection()

    def draw(self, screen):
        screen.blit(self.background, self.bg_rect)
        screen.blit(self.panel, self.panel_rect)

        shadow_surface = self.title_font.render(self.title_text, False, BROWN)
        shadow_rect = shadow_surface.get_rect(center=(self.panel_rect.centerx + 2, self.panel_rect.y + 12))

        title_surface = self.title_font.render(self.title_text, False, BLACK)
        title_rect = title_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 10))

        screen.blit(shadow_surface, shadow_rect)
        screen.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(screen)