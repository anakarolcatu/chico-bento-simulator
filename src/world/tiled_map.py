import pygame
import pytmx


class TiledMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename)

        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        self.width = self.tmx_data.width * self.tile_width
        self.height = self.tmx_data.height * self.tile_height

        self.collision_rects = []
        self.load_collisions()

    def load_collisions(self):
        for obj in self.tmx_data.objects:
            if obj.name == "Colisao":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.collision_rects.append(rect)

    def draw(self, screen, camera):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(
                            tile,
                            (
                                x * self.tmx_data.tilewidth - camera.x,
                                y * self.tmx_data.tileheight - camera.y
                            )
                        )