import pygame
from src.utils.spritesheet import get_sprite
from src.utils.ui_helper import nine_slice
from src.ui.buttons import Button


class PauseMenu:
    def __init__(self, font, title_font=None):
        self.font = font
        self.title_font = title_font or font

        self.is_open = False
        self.selected = 0
        self.options = ["CONTINUAR", "SALVAR", "CONTROLES", "SAIR"]

        sheet = pygame.image.load("assets/ui/Main_menu.png").convert_alpha()

        # painel
        panel_base = get_sprite(sheet, 97, 2, 33, 65)
        self.panel = nine_slice(panel_base, 320, 300, 4)
        self.panel_rect = self.panel.get_rect(center=(640, 360))

        # botões
        normal_button = get_sprite(sheet, 104, 130, 32, 15)
        selected_button = get_sprite(sheet, 8, 130, 32, 15)
        pressed_button = get_sprite(sheet, 56, 130, 32, 15)

        normal_button = pygame.transform.scale(normal_button, (190, 52))
        selected_button = pygame.transform.scale(selected_button, (190, 52))
        pressed_button = pygame.transform.scale(pressed_button, (190, 52))

        center_x = self.panel_rect.centerx
        start_y = self.panel_rect.y + 95
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
                return None

            elif event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self.update_selection()

            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self.update_selection()

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return self.options[self.selected]

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, button in enumerate(self.buttons):
                if button.rect.collidepoint(event.pos):
                    self.selected = i
                    self.update_selection()
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