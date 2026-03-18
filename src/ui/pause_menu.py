import pygame
from src.utils.spritesheet import get_sprite
from src.utils.ui_helper import nine_slice
from src.ui.buttons import Button


class PauseMenu:
    def __init__(self, game, font, title_font=None):
        self.game = game
        self.font = font
        self.title_font = title_font or font

        self.is_open = False
        self.selected = 0
        self.options = ["CONTINUAR", "SALVAR", "CONTROLES", "SAIR"]

        sheet = pygame.image.load("assets/ui/Main_menu.png").convert_alpha()
        buttons_sheet = pygame.image.load("assets/ui/Buttons.png").convert_alpha()

        # painel
        panel_base = get_sprite(sheet, 98, 4, 80, 168)
        self.panel = nine_slice(panel_base, 240, 300, 4)
        self.panel_rect = self.panel.get_rect(center=(640, 360))

        # botões
        normal_button = get_sprite(buttons_sheet, 307, 141, 44, 15)
        selected_button = get_sprite(buttons_sheet, 211, 141, 44, 15)
        pressed_button = get_sprite(buttons_sheet, 259, 142, 44, 15)

        normal_button = pygame.transform.scale(normal_button, (190, 52))
        selected_button = pygame.transform.scale(selected_button, (190, 52))
        pressed_button = pygame.transform.scale(pressed_button, (190, 52))

        center_x = self.panel_rect.centerx
        start_y = self.panel_rect.y + 90
        gap = 56

        self.buttons = [
            Button(normal_button, selected_button, pressed_button, center_x, start_y + i * gap, text, self.font, (20, 20, 20), (120, 70, 40))
            for i, text in enumerate(self.options)
        ]

        self.update_selection()

    def open(self):
        self.is_open = True
        self.selected = 0
        self.update_selection()

    def close(self):
        self.is_open = False

    def update_selection(self):
        for i, button in enumerate(self.buttons):
            if i == self.selected:
                button.set_state("selected")
            else:
                button.set_state("normal")

    def handle_event(self, event):
        if not self.is_open:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "CLOSE"

            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self.update_selection()
                self.game.audio.play_sound("menu_select")

            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self.update_selection()
                self.game.audio.play_sound("menu_select")

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.game.audio.play_sound("pause_menu")
                return self.options[self.selected]

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected = i
                    self.update_selection()
                    self.game.audio.play_sound("pause_menu")
                    return self.options[self.selected]

        return None

    def update_hover(self):
        if not self.is_open:
            return

        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.selected = i
                self.update_selection()

    def draw(self, screen):
        if not self.is_open:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        screen.blit(self.panel, self.panel_rect)

        title_surface = self.title_font.render("PAUSA", False, (20, 20, 20))
        title_rect = title_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 40))
        screen.blit(title_surface, title_rect)

        for button in self.buttons:
            button.draw(screen)