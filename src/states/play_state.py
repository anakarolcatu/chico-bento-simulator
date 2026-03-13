import pygame
from src.states.base_state import BaseState
from src.entities.player import Player
from src.states.menu_state import MenuState
from src.world.garden import Garden
from src.systems.inventory import Inventory
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from src.utils.spritesheet import get_sprite
from src.data.crops import CROPS
from src.ui.shop_overlay import ShopOverlay
from src.core.font_manager import FontManager

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
        self.font = FontManager.get(14)
        self.shop_title_font = FontManager.get(18)

        self.obstacles = [
            self.house_rect,
            self.shop_rect
        ]

        # Inventário
        self.inventory = Inventory(size=10)
        self.shop_overlay = ShopOverlay(self.inventory, self.font, self.shop_title_font)
        self.selected_slot = 0
        self.money = 20
        self.seed_price = 3
        self.inventory.add_item("seed_cebola", 5)
        self.inventory.add_item("seed_cenoura", 3)
        self.inventory.add_item("seed_trigo", 2)
        
        # fundo do inventário
        sheet = pygame.image.load("assets/ui/Action_panel.png").convert_alpha()
        panel_base = get_sprite(sheet, 12, 43, 169, 22)
        self.action_panel = pygame.transform.scale(panel_base, (560, 80))
        self.action_panel_rect = self.action_panel.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        self.slot_count = 10
        self.slot_width = 48
        self.slot_height = 48
        self.slot_start_x = self.action_panel_rect.x + 14
        self.slot_start_y = self.action_panel_rect.y + 22
        self.slot_spacing = 54

        # vendinha
        self.shop_interaction_rect = pygame.Rect(
            self.shop_rect.x,
            self.shop_rect.bottom,
            self.shop_rect.width,
            50
        )

    def handle_event(self, event):
        if self.shop_overlay.is_open:
            self.money = self.shop_overlay.handle_event(event, self.money)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state(MenuState(self.game))

            elif event.key == pygame.K_e:
                if self.player.hitbox.colliderect(self.shop_interaction_rect):
                    self.shop_overlay.open()
                else:
                    self.handle_garden_interaction()

            elif pygame.K_1 <= event.key <= pygame.K_9:
                self.selected_slot = event.key - pygame.K_1

            elif event.key == pygame.K_0:
                self.selected_slot = 9

    def handle_garden_interaction(self):
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

        if tile_pos is None:
            return

        row, col = tile_pos
        tile = self.garden.tiles[row][col]

        if tile["state"] == "empty":
            self.garden.hoe_tile(row, col)

        elif tile["state"] == "hoed":
            selected_item = self.inventory.get_selected_item(self.selected_slot)

            if selected_item in CROPS:
                consumed = self.inventory.consume_from_slot(self.selected_slot, 1)

                if consumed:
                    crop_data = CROPS[selected_item]
                    crop_type = crop_data["crop_name"]
                    growth_time = crop_data["growth_time"]
                    self.garden.plant_tile(row, col, crop_type, growth_time)

        elif tile["state"] == "grown":
            harvested_crop = self.garden.harvest_tile(row, col)

            if harvested_crop is not None:
                self.inventory.add_item(harvested_crop, 1)
    
    def update(self, dt):
        if not self.shop_overlay.is_open:
            self.player.update(dt, self.obstacles)
            self.garden.update(dt)

    def draw(self, screen):
        screen.fill((111, 183, 88))

        # casa
        pygame.draw.rect(screen, (160, 160, 170), self.house_rect, border_radius=8)
        house_text = self.font.render("Casa", True, (20, 20, 20))
        screen.blit(house_text, house_text.get_rect(center=self.house_rect.center))

        # vendinha
        pygame.draw.rect(screen, (220, 190, 110), self.shop_rect, border_radius=8)
        shop_text = self.font.render("Vendinha", True, (20, 20, 20))
        screen.blit(shop_text, shop_text.get_rect(center=self.shop_rect.center))

        # plantio
        garden_area = pygame.Rect(
            self.garden.x,
            self.garden.y,
            self.garden.cols * self.garden.tile_size,
            self.garden.rows * self.garden.tile_size
        )
        pygame.draw.rect(screen, (135, 92, 56), garden_area, border_radius=8)

        self.garden.draw(screen)
        self.player.draw(screen)

        hint = self.font.render("E: interagir | 1-0: selecionar slot | ESC: menu", True, (20, 20, 20))
        screen.blit(hint, (20, 20))
        # inventário
        screen.blit(self.action_panel, self.action_panel_rect)
        for i in range(self.slot_count):
            slot = self.inventory.get_slot(i)
            slot_x = self.slot_start_x + i * self.slot_spacing
            slot_y = self.slot_start_y

            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_width, self.slot_height)
            # debug para ver alinhamento
            # pygame.draw.rect(screen, (255, 0, 0), slot_rect, 1)

            if i == self.selected_slot:
                pygame.draw.rect(screen, (255, 230, 120), slot_rect, 2)

            if slot is not None:
                item_name = slot["item"]
                if item_name in CROPS:
                    color = CROPS[item_name]["color"]
                    pygame.draw.circle(screen, color, slot_rect.center, 8)

                else:
                    # produtos colhidos
                    crop_colors = {
                        "cebola": (40, 170, 40),
                        "cenoura": (255, 140, 60),
                        "milho": (240, 210, 70)
                    }

                    if item_name in crop_colors:
                        pygame.draw.circle(screen, crop_colors[item_name], slot_rect.center, 10)

                amount_text = self.font.render(str(slot["amount"]), False, (20, 20, 20))
                text_rect = amount_text.get_rect(bottomright=(slot_rect.right - 4, slot_rect.bottom - 2))
                screen.blit(amount_text, text_rect)

        money_text = self.font.render(f"Dinheiro: ${self.money}", True, (20, 20, 20))
        screen.blit(money_text, (20, 50))
        self.shop_overlay.draw(screen, self.money)
