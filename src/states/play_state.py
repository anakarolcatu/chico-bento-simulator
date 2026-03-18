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
from src.ui.pause_menu import PauseMenu
from src.ui.controls_overlay import ControlsOverlay
from src.systems.save_manager import SaveManager
from src.utils.asset_loader import AssetLoader

class PlayState(BaseState):
    def __init__(self, game):
        super().__init__(game)

        self.map = TiledMap("assets/maps/GameKit.tmx", scale=3)

        self.font = FontManager.get(14)
        self.font_small = FontManager.get(12)
        self.shop_title_font = FontManager.get(18)

        spawn_x, spawn_y = self.map.player_spawn
        self.player = Player(spawn_x, spawn_y)
        self.pause_menu = PauseMenu(self.game, self.font, self.shop_title_font)
        self.controls_overlay = ControlsOverlay(self.font, self.shop_title_font)

        # Grupo de layers para renderização
        self.background_layers = {
            "Ground",
            "Spots",
            "Plantio",
            "Road",
            "Grass",
            "Plates",
            "Grass_detail6",
            "Grass_details3",
            "Grass_details4",
            "Grass_details5",
        }

        self.depth_layers = {
            "Objects1",
            "Objects2",
            "Objects3",
            "Objects4",
            "Fence",
            "House_wall",
            "windows1",
            "windows2",
            "Loja",
            "Expositor",
            "Detalhes_loha",
            "cat",
        }

        self.foreground_layers = {
            "House_roof",
            "Grass_top_details",
            "Birds",
        }

        farm_rect = self.map.farm_area
        tile_size = self.map.scaled_tile_width

        cols = farm_rect.width // tile_size
        rows = farm_rect.height // tile_size

        self.garden = Garden(
            x=farm_rect.x,
            y=farm_rect.y,
            cols=cols,
            rows=rows,
            tile_size=tile_size,
            scale=self.map.scale
        )

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
        self.shop_overlay = ShopOverlay(self.inventory, self.font, self.shop_title_font, self.game.audio)
        self.selected_slot = 0
        self.money = 20
        self.inventory.add_item("seed_cebola", 5)
        self.inventory.add_item("seed_brocolis", 3)
        self.inventory.add_item("seed_trigo", 2)
        self.item_icons = AssetLoader.load_crop_icons((24, 24))
        
        # fundo do inventário
        sheet = AssetLoader.load_image("assets/ui/Action_panel.png")
        panel_base = get_sprite(sheet, 12, 43, 169, 22)
        money_panel = get_sprite(sheet, 13, 77, 22, 19)
        shop_sheet = AssetLoader.load_image("assets/ui/Shop.png")
        self.coin_img = get_sprite(shop_sheet, 483, 163, 11, 11)
        self.coin_img = pygame.transform.scale(self.coin_img, (18, 18))
        self.action_panel = pygame.transform.scale(panel_base, (560, 80))
        self.money_panel = pygame.transform.scale(money_panel, (72, 72))
        self.action_panel_rect = self.action_panel.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT))
        self.money_panel_rect = self.money_panel.get_rect(
            midright=(self.action_panel_rect.left - 10, self.action_panel_rect.centery)
        )
        self.slot_count = 10
        self.slot_width = 48
        self.slot_height = 48
        self.slot_start_x = self.action_panel_rect.x + 14
        self.slot_start_y = self.action_panel_rect.y + 22
        self.slot_spacing = 54

        # vendinha
        self.shop_interaction_rect = self.map.shop_trigger

        # Salvar jogo
        self.feedback_message = ""
        self.feedback_timer = 0
        self.feedback_duration = 2.0

        # sons 
        self.walk_sound_timer = 0
        self.walk_sound_interval = 0.36

    def handle_event(self, event):
        if self.shop_overlay.is_open:
            self.money = self.shop_overlay.handle_event(event, self.money)
            return
        
        if self.controls_overlay.is_open:
            closed = self.controls_overlay.handle_event(event)

            if closed:
                self.pause_menu.open()

            return
        
        if self.pause_menu.is_open:
            action = self.pause_menu.handle_event(event)

            if action == "CLOSE":
                self.game.audio.resume_music()

            if action == "CONTINUAR":
                self.pause_menu.close()
                self.game.audio.resume_music()

            elif action == "SALVAR":
                self.save_game()
                self.pause_menu.close()
                self.game.audio.resume_music()
                self.show_feedback("JOGO SALVO")

            elif action == "CONTROLES":
                self.pause_menu.close()
                self.controls_overlay.open()

            elif action == "SAIR":
                self.game.change_state(MenuState(self.game))

            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.pause_menu.open()
                self.game.audio.pause_music()
                self.game.audio.play_sound("pause_menu")

            elif event.key == pygame.K_e:
                if self.player.hitbox.colliderect(self.shop_interaction_rect):
                    self.shop_overlay.open()
                    self.game.audio.play_sound("pause_menu")
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
                    self.game.audio.play_sound("planting")

        elif tile["state"] == "grown":
            harvested_crop = self.garden.harvest_tile(row, col)

            if harvested_crop is not None:
                self.inventory.add_item(harvested_crop, 1)
                self.game.audio.play_sound("harvest")

    def save_game(self):
        SaveManager.save_game(self)
        print("Jogo salvo com sucesso.")


    def load_game_data(self, data):
        self.player.x = data["player"]["x"]
        self.player.y = data["player"]["y"]
        self.player.direction = data["player"]["direction"]

        self.player.rect.center = (round(self.player.x), round(self.player.y))
        self.player.hitbox.center = (self.player.x, self.player.y + 18)

        self.money = data["money"]
        self.selected_slot = data["selected_slot"]

        self.inventory.load_from_dict(data["inventory"])
        self.garden.load_from_dict(data["garden"])

    def show_feedback(self, message):
        self.feedback_message = message
        self.feedback_timer = self.feedback_duration


    def draw_inventory_item_icon(self, screen, item_name, slot_rect):
        icon = self.item_icons.get(item_name)

        if icon is None:
            return False

        icon_rect = icon.get_rect(center=slot_rect.center)
        screen.blit(icon, icon_rect)
        return True
    
    def update(self, dt):
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_message = ""
                self.feedback_timer = 0

        if self.shop_overlay.is_open:
            return
        
        if self.controls_overlay.is_open:
            return

        if self.pause_menu.is_open:
            self.pause_menu.update_hover()
            return

        self.player.update(dt, self.obstacles, self.map.width, self.map.height)
        self.garden.update(dt)
        self.camera.update(self.player.rect)

        if self.player.is_moving:
            self.walk_sound_timer -= dt
            if self.walk_sound_timer <= 0:
                self.game.audio.play_sound("steps")
                self.walk_sound_timer = self.walk_sound_interval
        else:
            self.walk_sound_timer = 0

    def draw(self, screen):
        screen.fill((0, 0, 0))

        self.map.draw_layer_group(screen, self.camera, self.background_layers)
        self.garden.draw(screen, self.camera)

        render_list = []
        render_list.extend(self.map.get_render_tiles_from_layers(self.depth_layers))
        render_list.append({
            "image": self.player.image,
            "rect": self.player.rect,
            "depth": self.player.hitbox.bottom
        })

        render_list.sort(key=lambda obj: obj["depth"])

        for obj in render_list:
            screen.blit(obj["image"], self.camera.apply(obj["rect"]))

        self.map.draw_layer_group(screen, self.camera, self.foreground_layers)

        screen.blit(self.action_panel, self.action_panel_rect)
        screen.blit(self.money_panel, self.money_panel_rect)

        money_surface = self.font.render(str(self.money), False, (20, 20, 20))

        coin_rect = self.coin_img.get_rect(
            midleft=(self.money_panel_rect.x + 12, self.money_panel_rect.centery)
        )

        money_rect = money_surface.get_rect(
            midleft=(coin_rect.right + 6, coin_rect.centery)
        )

        screen.blit(self.coin_img, coin_rect)
        screen.blit(money_surface, money_rect)
        
        for i in range(self.slot_count):
            slot = self.inventory.get_slot(i)
            slot_x = self.slot_start_x + i * self.slot_spacing
            slot_y = self.slot_start_y

            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_width, self.slot_height)

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

        if self.feedback_message:
            feedback_surface = self.font.render(self.feedback_message, False, (20, 20, 20))
            feedback_rect = feedback_surface.get_rect(center=(SCREEN_WIDTH // 2, 40))

            shadow_surface = self.font.render(self.feedback_message, False, (255, 255, 255))
            shadow_rect = shadow_surface.get_rect(center=(feedback_rect.centerx + 2, feedback_rect.centery + 2))

            screen.blit(shadow_surface, shadow_rect)
            screen.blit(feedback_surface, feedback_rect)

        self.shop_overlay.draw(screen, self.money)
        self.pause_menu.draw(screen)
        self.controls_overlay.draw(screen)