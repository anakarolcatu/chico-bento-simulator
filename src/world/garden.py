import pygame
from src.data.crops import CROPS
from src.utils.spritesheet import get_sprite

class Garden:
    def __init__(self, x, y, cols, rows, tile_size, scale=1):
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size
        self.scale = scale
        self.plant_stage_cache = {}
        self.hoed_tile = self.create_hoed_tile()
        self.load_plant_stage_sprites()

        self.tiles = []
        for row in range(rows):
            row_tiles = []
            for col in range(cols):
                row_tiles.append({
                    "state": "empty",
                    "growth_timer": 0,
                    "growth_time": 0,
                    "crop_type": None
                })
            self.tiles.append(row_tiles)

    def get_tile_rect(self, row, col):
        return pygame.Rect(
            self.x + col * self.tile_size,
            self.y + row * self.tile_size,
            self.tile_size,
            self.tile_size
        )

    def get_tile_at_pixel(self, px, py):
        if px < self.x or py < self.y:
            return None

        col = (px - self.x) // self.tile_size
        row = (py - self.y) // self.tile_size

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return int(row), int(col)

        return None
    
    def create_hoed_tile(self):
        tile = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)

        pygame.draw.rect(tile, (120, 78, 45), (0, 0, self.tile_size, self.tile_size), border_radius=4)

        line_color = (95, 58, 30)
        padding_x = 8
        spacing = 10

        y = 10
        while y < self.tile_size - 6:
            pygame.draw.line(tile, line_color, (padding_x, y), (self.tile_size - padding_x, y), 2)
            y += spacing

        return tile
    
    def load_plant_stage_sprites(self):
        loaded_sheets = {}

        def get_sheet(path):
            if path not in loaded_sheets:
                loaded_sheets[path] = pygame.image.load(path).convert_alpha()
            return loaded_sheets[path]

        for seed_name, crop_data in CROPS.items():
            if "plant_sheet" not in crop_data or "growth_stages" not in crop_data:
                continue

            sheet = get_sheet(crop_data["plant_sheet"])
            crop_name = crop_data["crop_name"]

            stage_surfaces = []

            for x, y, w, h in crop_data["growth_stages"]:
                sprite = get_sprite(sheet, x, y, w, h)

                scaled_w = int(w * self.scale)
                scaled_h = int(h * self.scale)
                sprite = pygame.transform.scale(sprite, (scaled_w, scaled_h))

                stage_surfaces.append(sprite)

            self.plant_stage_cache[crop_name] = stage_surfaces

    def get_stage_index(self, tile):
        if tile["state"] == "grown":
            return 2

        if tile["state"] != "planted":
            return None

        if tile["growth_time"] <= 0:
            return 0

        progress = tile["growth_timer"] / tile["growth_time"]

        if progress < 0.34:
            return 0
        elif progress < 0.67:
            return 1
        else:
            return 2

    def hoe_tile(self, row, col):
        if self.tiles[row][col]["state"] == "empty":
            self.tiles[row][col]["state"] = "hoed"

    def plant_tile(self, row, col, crop_type, growth_time):
        tile = self.tiles[row][col]
        if tile["state"] == "hoed":
            tile["state"] = "planted"
            tile["growth_timer"] = 0
            tile["growth_time"] = growth_time
            tile["crop_type"] = crop_type

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "cols": self.cols,
            "rows": self.rows,
            "tile_size": self.tile_size,
            "scale": self.scale,
            "tiles": self.tiles
        }

    def load_from_dict(self, data):
        self.x = data["x"]
        self.y = data["y"]
        self.cols = data["cols"]
        self.rows = data["rows"]
        self.tile_size = data["tile_size"]
        self.scale = data["scale"]
        self.tiles = data["tiles"]

        self.hoed_tile = self.create_hoed_tile()
        self.load_plant_stage_sprites()

    def update(self, dt):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[row][col]

                if tile["state"] == "planted":
                    tile["growth_timer"] += dt

                    if tile["growth_timer"] >= tile["growth_time"]:
                        tile["state"] = "grown"
    
    def harvest_tile(self, row, col):
        tile = self.tiles[row][col]

        if tile["state"] == "grown":
            harvested_crop = tile["crop_type"]

            tile["state"] = "hoed"
            tile["growth_timer"] = 0
            tile["growth_time"] = 0
            tile["crop_type"] = None
            return harvested_crop
        return None


    def draw(self, screen, camera):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[row][col]

                world_rect = self.get_tile_rect(row, col)
                screen_rect = camera.apply(world_rect)

                # solo arado
                if tile["state"] in ("hoed", "planted", "grown"):
                    screen.blit(self.hoed_tile, screen_rect.topleft)

                # planta
                if tile["state"] in ("planted", "grown") and tile["crop_type"]:
                    stage_index = self.get_stage_index(tile)

                    if stage_index is not None:
                        stages = self.plant_stage_cache.get(tile["crop_type"])

                        if stages and stage_index < len(stages):
                            plant_img = stages[stage_index]

                            plant_rect = plant_img.get_rect(
                                midbottom=(screen_rect.centerx, screen_rect.bottom)
                            )
                            screen.blit(plant_img, plant_rect)