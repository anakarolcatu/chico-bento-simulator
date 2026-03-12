import pygame


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
                    "state": "empty"
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

    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                tile = self.tiles[row][col]
                rect = self.get_tile_rect(row, col)

                if tile["state"] == "empty":
                    color = (110, 70, 40)
                elif tile["state"] == "hoed":
                    color = (85, 52, 28)
                else:
                    color = (110, 70, 40)

                inner_rect = rect.inflate(-8, -8)
                pygame.draw.rect(screen, color, inner_rect, border_radius=4)