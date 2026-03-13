import pygame
from src.states.base_state import BaseState
from src.entities.player import Player
from src.states.menu_state import MenuState
from src.world.garden import Garden
from src.systems.inventory import Inventory
from src.ui.shop_ui import ShopUI


class PlayState(BaseState):
    def __init__(self, game):
        super().__init__(game)

        self.player = Player(500, 420)

        self.house_rect = pygame.Rect(120, 80, 230, 180)
        self.shop_rect = pygame.Rect(800, 90, 200, 160)

        self.garden = Garden(
            x=360,
            y=280,
            cols=6,
            rows=3,
            tile_size=60
        )

        self.obstacles = [
            self.house_rect,
            self.shop_rect
        ]

        self.inventory = Inventory()
        self.shop_ui = ShopUI(self.inventory)

        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.hud_font = pygame.font.SysFont("arial", 18, bold=True)

    # ------------------------------------------------------------------
    def _near_shop(self):
        """Return True when the player's hitbox is close enough to open the shop."""
        return self.player.hitbox.inflate(80, 80).colliderect(self.shop_rect)

    # ------------------------------------------------------------------
    def handle_event(self, event):
        # Delegate all input to the shop overlay while it is open
        if self.shop_ui.is_open:
            self.shop_ui.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(MenuState(self.game))

            elif event.key == pygame.K_e:
                # Open shop when nearby
                if self._near_shop():
                    self.shop_ui.open()
                    return

                # Otherwise interact with the garden
                px = self.player.hitbox.centerx
                py = self.player.hitbox.centery

                offset = self.garden.tile_size // 2

                if self.player.direction == "up":
                    py -= offset
                elif self.player.direction == "down":
                    py += offset
                elif self.player.direction == "left":
                    px -= offset
                elif self.player.direction == "right":
                    px += offset

                tile_pos = self.garden.get_tile_at_pixel(px, py)

                if tile_pos is not None:
                    row, col = tile_pos
                    tile = self.garden.tiles[row][col]

                    if tile["state"] == "empty":
                        self.garden.hoe_tile(row, col)
                    elif tile["state"] == "hoed":
                        if self.inventory.use_seed():
                            self.garden.plant_tile(row, col)
                    elif tile["state"] == "grown":
                        self.garden.harvest_tile(row, col)
                        self.inventory.add_crop(1)

    def update(self, dt):
        if not self.shop_ui.is_open:
            self.player.update(dt, self.obstacles)
        self.garden.update(dt)
        self.shop_ui.update(dt)

    def draw(self, screen):
        screen.fill((111, 183, 88))

        pygame.draw.rect(screen, (160, 160, 170), self.house_rect, border_radius=8)
        house_text = self.font.render("Casa", True, (20, 20, 20))
        screen.blit(house_text, house_text.get_rect(center=self.house_rect.center))

        pygame.draw.rect(screen, (220, 190, 110), self.shop_rect, border_radius=8)
        shop_text = self.font.render("Vendinha", True, (20, 20, 20))
        screen.blit(shop_text, shop_text.get_rect(center=self.shop_rect.center))

        # Show "E: loja" label when the player is near the shop
        if self._near_shop():
            near_hint = self.hud_font.render("E: abrir loja", True, (20, 20, 20))
            screen.blit(near_hint, near_hint.get_rect(center=(self.shop_rect.centerx, self.shop_rect.bottom + 18)))

        garden_area = pygame.Rect(
            self.garden.x,
            self.garden.y,
            self.garden.cols * self.garden.tile_size,
            self.garden.rows * self.garden.tile_size
        )
        pygame.draw.rect(screen, (135, 92, 56), garden_area, border_radius=8)

        garden_text = self.font.render("Jardim", True, (240, 240, 240))
        screen.blit(garden_text, garden_text.get_rect(center=(garden_area.centerx, garden_area.y + 20)))

        self.garden.draw(screen)

        self.player.draw(screen)

        # HUD – coins, seeds, crops
        hud_text = (
            f"Moedas: {self.inventory.coins}   "
            f"Sementes: {self.inventory.seeds}   "
            f"Colheitas: {self.inventory.crops}"
        )
        hud = self.hud_font.render(hud_text, True, (20, 20, 20))
        screen.blit(hud, (20, 20))

        # Context hint at the bottom
        if self._near_shop():
            hint_str = "E: abrir loja | ESC: voltar"
        else:
            hint_str = "E: arar/plantar/colher | ESC: voltar"
        hint = self.font.render(hint_str, True, (20, 20, 20))
        screen.blit(hint, (20, 46))

        # Draw the shop overlay on top of everything
        self.shop_ui.draw(screen)