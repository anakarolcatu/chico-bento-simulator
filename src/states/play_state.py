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
from src.world.tiled_map import TiledMap
from src.world.camera import Camera

class PlayState(BaseState):
    def __init__(self, game):
        super().__init__(game)

        self.player = Player(500, 420)

        self.house_rect = pygame.Rect(120, 80, 230, 180)
        self.shop_rect = pygame.Rect(800, 90, 200, 160)
        self.map = TiledMap("assets/maps/GameKit.tmx")

        self.garden = Garden(
            x=360,
            y=280,
            cols=6,
            rows=3,
            tile_size=60
        )
        self.font = FontManager.get(14)
        self.font_small = FontManager.get(12)
        self.shop_title_font = FontManager.get(18)

        self.obstacles = self.map.collision_rects

        # Camera
        self.camera = Camera(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.map.width,
            self.map.height
        )

        # Inventário
        self.inventory = Inventory(size=10)
        self.shop_overlay = ShopOverlay(self.inventory, self.font, self.shop_title_font)
        self.selected_slot = 0
        self.money = 20
        self.seed_price = 3
        self.inventory.add_item("seed_cebola", 5)
        self.inventory.add_item("seed_brocolis", 3)
        self.inventory.add_item("seed_trigo", 2)
        self.item_icons = self.load_item_icons()
        
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

    def load_item_icons(self):
        icons = {}
        loaded_sheets = {}

        def get_sheet(path):
            if path not in loaded_sheets:
                loaded_sheets[path] = pygame.image.load(path).convert_alpha()
            return loaded_sheets[path]

        for seed_name, crop_data in CROPS.items():
            # ícone da semente
            if "seed_sheet" in crop_data and "seed_icon" in crop_data:
                seed_sheet = get_sheet(crop_data["seed_sheet"])
                x, y, w, h = crop_data["seed_icon"]

                icon = get_sprite(seed_sheet, x, y, w, h)
                icon = pygame.transform.scale(icon, (24, 24))
                icons[seed_name] = icon

            # ícone da colheita
            if "crop_sheet" in crop_data and "crop_icon" in crop_data:
                crop_sheet = get_sheet(crop_data["crop_sheet"])
                x, y, w, h = crop_data["crop_icon"]

                icon = get_sprite(crop_sheet, x, y, w, h)
                icon = pygame.transform.scale(icon, (24, 24))
                icons[crop_data["crop_name"]] = icon

        return icons


    def draw_inventory_item_icon(self, screen, item_name, slot_rect):
        icon = self.item_icons.get(item_name)

        if icon is None:
            return False

        icon_rect = icon.get_rect(center=slot_rect.center)
        screen.blit(icon, icon_rect)
        return True
    
    def update(self, dt):
        if not self.shop_overlay.is_open:
            self.player.update(dt, self.obstacles)
            self.garden.update(dt)
            self.camera.update(self.player.rect)

    def draw(self, screen):
        self.map.draw(screen)
        self.player.draw(screen)
        self.map.draw(screen, self.camera)

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

                drawn = self.draw_inventory_item_icon(screen, item_name, slot_rect)

                if not drawn:
                    if item_name in CROPS:
                        color = CROPS[item_name]["color"]
                        pygame.draw.circle(screen, color, slot_rect.center, 8)
                    else:
                        pygame.draw.circle(screen, (40, 170, 40), slot_rect.center, 10)

                if slot["amount"] > 1:
                    amount_surface = self.font_small.render(str(slot["amount"]), False, (20, 20, 20))
                    amount_rect = amount_surface.get_rect(
                        bottomright=(slot_rect.right - 4, slot_rect.bottom - 3)
                    )
                    shadow_surface = self.font_small.render(str(slot["amount"]), False, (255, 255, 255))
                    shadow_rect = shadow_surface.get_rect(
                        bottomright=(slot_rect.right - 3, slot_rect.bottom - 2)
                    )
                    screen.blit(shadow_surface, shadow_rect)
                    screen.blit(amount_surface, amount_rect)

        money_text = self.font.render(f"Dinheiro: ${self.money}", True, (20, 20, 20))
        screen.blit(money_text, (20, 50))

        self.shop_overlay.draw(screen, self.money)
