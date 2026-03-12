import pygame
from src.states.base_state import BaseState
from src.entities.player import Player
from src.states.menu_state import MenuState
from src.world.garden import Garden


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

        self.font = pygame.font.SysFont("arial", 22, bold=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(MenuState(self.game))

            elif event.key == pygame.K_e:
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
                    self.garden.hoe_tile(row, col)

    def update(self, dt):
        self.player.update(dt, self.obstacles)

    def draw(self, screen):
        screen.fill((111, 183, 88))

        pygame.draw.rect(screen, (160, 160, 170), self.house_rect, border_radius=8)
        house_text = self.font.render("Casa", True, (20, 20, 20))
        screen.blit(house_text, house_text.get_rect(center=self.house_rect.center))

        pygame.draw.rect(screen, (220, 190, 110), self.shop_rect, border_radius=8)
        shop_text = self.font.render("Vendinha", True, (20, 20, 20))
        screen.blit(shop_text, shop_text.get_rect(center=self.shop_rect.center))

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

        hint = self.font.render("E para arar | ESC para voltar", True, (20, 20, 20))
        screen.blit(hint, (20, 20))