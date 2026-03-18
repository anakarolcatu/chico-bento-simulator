import pygame
from src.utils.spritesheet import get_sprite
from src.utils.ui_helper import nine_slice


class ControlsOverlay:
    def __init__(self, font, title_font=None):
        self.font = font
        self.title_font = title_font or font
        self.is_open = False

        sheet = pygame.image.load("assets/ui/Settings.png").convert_alpha()

        panel_base = get_sprite(sheet, 7, 0, 98, 149)
        self.panel = nine_slice(panel_base, 420, 340, 4)
        self.panel_rect = self.panel.get_rect(center=(640, 360))

        self.lines = [
            "WASD / SETAS - ANDAR",
            "E - INTERAGIR",
            "1-0 - SELECIONAR SLOT",
            "ESC - PAUSA / MENU",
            "ENTER - CONFIRMAR",
            "TAB - TROCAR LOJA"
        ]

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False

    def handle_event(self, event):
        if not self.is_open:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
                self.close()
                return True

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.close()
            return True

        return False

    def draw(self, screen):
        if not self.is_open:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        screen.blit(self.panel, self.panel_rect)

        title_surface = self.title_font.render("CONTROLES", False, (20, 20, 20))
        title_rect = title_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.y + 38))
        screen.blit(title_surface, title_rect)

        start_y = self.panel_rect.y + 95
        line_gap = 34

        for i, line in enumerate(self.lines):
            text_surface = self.font.render(line, False, (20, 20, 20))
            text_rect = text_surface.get_rect(center=(self.panel_rect.centerx, start_y + i * line_gap))
            screen.blit(text_surface, text_rect)

        hint_surface = self.font.render("ESC OU ENTER PARA FECHAR", False, (120, 70, 40))
        hint_rect = hint_surface.get_rect(center=(self.panel_rect.centerx, self.panel_rect.bottom - 28))
        screen.blit(hint_surface, hint_rect)