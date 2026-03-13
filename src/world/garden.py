import pygame
from src.data.crops import CROPS

class Garden:
    def __init__(self, x, y, cols, rows, tile_size):
        self.x = x
        self.y = y
        self.cols = cols
        self.rows = rows
        self.tile_size = tile_size

        self.tiles = []
        for row in range(rows):
            row_tiles = []
            for col in range(cols):
                row_tiles.append({
                    "state": "empty",
                    "growth_timer": 0, 
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


    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[row][col]
                rect = self.get_tile_rect(row, col)
                inner_rect = rect.inflate(-8, -8)

                if tile["state"] == "empty":
                    color = (110, 70, 40)

                elif tile["state"] in ("hoed", "planted", "grown"):
                    color = (85, 52, 28)

                else:
                    color = (110, 70, 40)

                pygame.draw.rect(screen, color, inner_rect, border_radius=4)

                if tile["state"] == "planted":
                    cx = rect.centerx
                    cy = rect.centery + 4
                    plant_color = (40, 170, 40)
                    for seed_name, crop_data in CROPS.items():
                        if crop_data["crop_name"] == tile["crop_type"]:
                            plant_color = crop_data["color"]
                            break
                    pygame.draw.circle(screen, plant_color, (cx, cy), 6)

                elif tile["state"] == "grown":
                    cx = rect.centerx
                    cy = rect.centery + 2
                    plant_color = (40, 170, 40)
                    for seed_name, crop_data in CROPS.items():
                        if crop_data["crop_name"] == tile["crop_type"]:
                            plant_color = crop_data["color"]
                            break

                    pygame.draw.rect(screen, (30, 120, 30), (cx - 4, cy - 16, 8, 10), border_radius=2)
                    pygame.draw.circle(screen, plant_color, (cx, cy), 10)