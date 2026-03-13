import pygame
from src.utils.spritesheet import get_sprite
from src.core.font_manager import FontManager
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE


class ShopUI:
    def __init__(self, inventory):
        self.inventory = inventory
        self.is_open = False

        # Navigation: side 0=comprar, 1=vender; action_idx=selected button
        self.side = 0
        self.action_idx = 0

        # Load Shop.png and extract Panel 1 (x=7, y=0, w=118, h=149) as panel base
        self.shop_sheet = pygame.image.load("assets/ui/Shop.png").convert_alpha()
        panel_base = get_sprite(self.shop_sheet, 7, 0, 118, 149)
        self._panel_surf = pygame.transform.scale(panel_base, (240, 320))

        # Load Buttons.png (same as menu) for action buttons
        button_sheet = pygame.image.load("assets/ui/Buttons.png").convert_alpha()
        btn_normal = pygame.transform.scale(get_sprite(button_sheet, 104, 130, 32, 15), (160, 34))
        btn_selected = pygame.transform.scale(get_sprite(button_sheet, 8, 130, 32, 15), (160, 34))
        btn_pressed = pygame.transform.scale(get_sprite(button_sheet, 56, 130, 32, 15), (160, 34))
        self._btn = {"normal": btn_normal, "selected": btn_selected, "pressed": btn_pressed}

        # Fonts
        self.font = FontManager.get(13)
        self.title_font = FontManager.get(18)
        self.hint_font = FontManager.get(11)

        # Window layout: two 240x320 panels with a 20px gap, centred on screen
        panel_w, panel_h = 240, 320
        gap = 20
        total_w = panel_w * 2 + gap
        self.left_x = (SCREEN_WIDTH - total_w) // 2
        self.right_x = self.left_x + panel_w + gap
        self.panel_y = (SCREEN_HEIGHT - panel_h) // 2

        # Action labels for each side
        self._buy_labels = ["Comprar 1", "Comprar 5"]
        self._sell_labels = ["Vender 1", "Vender Tudo"]

        # Feedback message
        self.message = ""
        self._message_timer = 0.0

    # ------------------------------------------------------------------
    def open(self):
        self.is_open = True
        self.side = 0
        self.action_idx = 0
        self.message = ""
        self._message_timer = 0.0

    def close(self):
        self.is_open = False

    # ------------------------------------------------------------------
    def handle_event(self, event):
        if not self.is_open:
            return

        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_ESCAPE:
            self.close()
        elif event.key == pygame.K_LEFT:
            self.side = 0
            self.action_idx = 0
        elif event.key == pygame.K_RIGHT:
            self.side = 1
            self.action_idx = 0
        elif event.key == pygame.K_UP:
            self.action_idx = max(0, self.action_idx - 1)
        elif event.key == pygame.K_DOWN:
            max_idx = len(self._buy_labels if self.side == 0 else self._sell_labels) - 1
            self.action_idx = min(max_idx, self.action_idx + 1)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
            self._execute_action()

    def _execute_action(self):
        inv = self.inventory
        if self.side == 0:
            # Buy seeds
            quantities = [1, 5]
            ok = inv.buy_seeds(quantities[self.action_idx])
            self.message = "Comprado!" if ok else "Moedas insuficientes!"
        else:
            # Sell crops
            quantities = [1, inv.crops]
            ok = inv.sell_crops(quantities[self.action_idx])
            self.message = "Vendido!" if ok else "Sem colheitas!"
        self._message_timer = 2.0

    # ------------------------------------------------------------------
    def update(self, dt):
        if self._message_timer > 0:
            self._message_timer -= dt
            if self._message_timer <= 0:
                self.message = ""

    # ------------------------------------------------------------------
    def draw(self, screen):
        if not self.is_open:
            return

        # Dim the background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        # Draw panel backgrounds
        screen.blit(self._panel_surf, (self.left_x, self.panel_y))
        screen.blit(self._panel_surf, (self.right_x, self.panel_y))

        self._draw_buy_side(screen)
        self._draw_sell_side(screen)

        # Bottom hint
        hint_text = (
            "← → : mudar painel   |   ↑ ↓ : navegar   |   ENTER: confirmar   |   ESC: fechar"
        )
        hint = self.hint_font.render(hint_text, True, WHITE)
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, self.panel_y + 320 + 18)))

        # Centred feedback message
        if self.message:
            if self.message in ("Comprado!", "Vendido!"):
                msg_color = (60, 200, 80)
            else:
                msg_color = (220, 60, 60)
            msg = self.font.render(self.message, True, msg_color)
            screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH // 2, self.panel_y + 320 + 40)))

    # ------------------------------------------------------------------
    def _draw_buy_side(self, screen):
        x = self.left_x
        y = self.panel_y
        inv = self.inventory

        # Title
        title = self.title_font.render("COMPRAR", False, (41, 64, 64))
        screen.blit(title, title.get_rect(center=(x + 120, y + 22)))

        # Divider
        pygame.draw.line(screen, (41, 64, 64), (x + 15, y + 40), (x + 225, y + 40), 2)

        # Item info
        screen.blit(self.font.render("Sementes", True, BLACK), (x + 20, y + 55))
        screen.blit(
            self.font.render(f"Preço: {inv.SEED_PRICE} moedas / ud", True, (80, 60, 30)),
            (x + 20, y + 78),
        )
        screen.blit(
            self.font.render(f"Sementes em mão: {inv.seeds}", True, (40, 130, 40)),
            (x + 20, y + 101),
        )
        screen.blit(
            self.font.render(f"Moedas: {inv.coins}", True, (170, 130, 20)),
            (x + 20, y + 124),
        )

        # Action buttons
        for i, label in enumerate(self._buy_labels):
            btn_y = y + 175 + i * 50
            selected = self.side == 0 and self.action_idx == i
            key = "selected" if selected else "normal"
            btn_rect = self._btn[key].get_rect(center=(x + 120, btn_y))
            screen.blit(self._btn[key], btn_rect)
            color = (180, 120, 20) if selected else BLACK
            txt = self.font.render(label, True, color)
            screen.blit(txt, txt.get_rect(center=(x + 120, btn_y)))

        # Panel label when focused
        if self.side == 0:
            indicator = self.hint_font.render("▼ painel ativo", True, (41, 64, 64))
            screen.blit(indicator, indicator.get_rect(center=(x + 120, y + 300)))

    def _draw_sell_side(self, screen):
        x = self.right_x
        y = self.panel_y
        inv = self.inventory

        # Title
        title = self.title_font.render("VENDER", False, (41, 64, 64))
        screen.blit(title, title.get_rect(center=(x + 120, y + 22)))

        # Divider
        pygame.draw.line(screen, (41, 64, 64), (x + 15, y + 40), (x + 225, y + 40), 2)

        # Item info
        screen.blit(self.font.render("Colheita", True, BLACK), (x + 20, y + 55))
        screen.blit(
            self.font.render(f"Preço: {inv.CROP_PRICE} moedas / ud", True, (80, 60, 30)),
            (x + 20, y + 78),
        )
        screen.blit(
            self.font.render(f"Colheitas em mão: {inv.crops}", True, (40, 130, 40)),
            (x + 20, y + 101),
        )
        screen.blit(
            self.font.render(f"Moedas: {inv.coins}", True, (170, 130, 20)),
            (x + 20, y + 124),
        )

        # Action buttons
        for i, label in enumerate(self._sell_labels):
            btn_y = y + 175 + i * 50
            selected = self.side == 1 and self.action_idx == i
            key = "selected" if selected else "normal"
            btn_rect = self._btn[key].get_rect(center=(x + 120, btn_y))
            screen.blit(self._btn[key], btn_rect)
            color = (180, 120, 20) if selected else BLACK
            txt = self.font.render(label, True, color)
            screen.blit(txt, txt.get_rect(center=(x + 120, btn_y)))

        # Panel label when focused
        if self.side == 1:
            indicator = self.hint_font.render("▼ painel ativo", True, (41, 64, 64))
            screen.blit(indicator, indicator.get_rect(center=(x + 120, y + 300)))
