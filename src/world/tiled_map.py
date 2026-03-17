import pygame
import pytmx


class TiledMap:
    def __init__(self, filename, scale=4):
        self.tmx_data = pytmx.load_pygame(filename)
        self.scale = scale

        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight

        self.scaled_tile_width = self.tile_width * self.scale
        self.scaled_tile_height = self.tile_height * self.scale

        self.width = self.tmx_data.width * self.scaled_tile_width
        self.height = self.tmx_data.height * self.scaled_tile_height

        self.player_spawn = (100, 100)
        self.shop_trigger = None
        self.farm_area = None

        for obj in self.tmx_data.objects:
            if obj.name == "PlayerSpawn":
                self.player_spawn = (
                    (obj.x + obj.width / 2) * self.scale,
                    (obj.y + obj.height / 2) * self.scale
                )
            elif obj.name == "ShopTrigger":
                self.shop_trigger = pygame.Rect(
                    obj.x * self.scale,
                    obj.y * self.scale,
                    obj.width * self.scale,
                    obj.height * self.scale
                )
            elif obj.name == "FarmArea":
                self.farm_area = pygame.Rect(
                    obj.x * self.scale,
                    obj.y * self.scale,
                    obj.width * self.scale,
                    obj.height * self.scale
                )

        self.collision_rects = []
        self.load_collisions()

    def load_collisions(self):
        collision_layer = self.tmx_data.get_layer_by_name("Colisao")

        for obj in collision_layer:
            rect = pygame.Rect(
                obj.x * self.scale,
                obj.y * self.scale,
                obj.width * self.scale,
                obj.height * self.scale
            )
            self.collision_rects.append(rect)

    def get_render_tiles(self):
        render_tiles = []

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile:
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (self.scaled_tile_width, self.scaled_tile_height)
                        )

                        world_x = x * self.scaled_tile_width
                        world_y = y * self.scaled_tile_height

                        depth = world_y + self.scaled_tile_height

                        render_tiles.append({
                            "image": scaled_tile,
                            "rect": pygame.Rect(
                                world_x,
                                world_y,
                                self.scaled_tile_width,
                                self.scaled_tile_height
                            ),
                            "depth": depth
                        })

        return render_tiles
    
    def draw_layer_group(self, screen, camera, layer_names):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data") and layer.name in layer_names:
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (self.scaled_tile_width, self.scaled_tile_height)
                        )

                        world_x = x * self.scaled_tile_width
                        world_y = y * self.scaled_tile_height

                        rect = pygame.Rect(
                            world_x,
                            world_y,
                            self.scaled_tile_width,
                            self.scaled_tile_height
                        )

                        screen.blit(scaled_tile, camera.apply(rect))

    def get_render_tiles_from_layers(self, layer_names):
        render_tiles = []

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data") and layer.name in layer_names:
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile:
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (self.scaled_tile_width, self.scaled_tile_height)
                        )

                        world_x = x * self.scaled_tile_width
                        world_y = y * self.scaled_tile_height

                        depth = world_y + self.scaled_tile_height

                        render_tiles.append({
                            "image": scaled_tile,
                            "rect": pygame.Rect(
                                world_x,
                                world_y,
                                self.scaled_tile_width,
                                self.scaled_tile_height
                            ),
                            "depth": depth
                        })

        return render_tiles

    def draw(self, screen, camera):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "data"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)

                    if tile:
                        scaled_tile = pygame.transform.scale(
                            tile,
                            (self.scaled_tile_width, self.scaled_tile_height)
                        )

                        screen.blit(
                            scaled_tile,
                            (
                                x * self.scaled_tile_width - camera.x,
                                y * self.scaled_tile_height - camera.y
                            )
                        )