class Camera:
    def __init__(self, screen_width, screen_height, world_width, world_height):
        self.w = screen_width
        self.h = screen_height

        self.world_w = world_width
        self.world_h = world_height

        self.x = 0
        self.y = 0

    def update(self, target_rect):
        self.x = target_rect.centerx - self.w // 2
        self.y = target_rect.centery - self.h // 2

        self.x = max(0, min(self.x, self.world_w - self.w))
        self.y = max(0, min(self.y, self.world_h - self.h))

    def apply(self, rect):
        return rect.move(-self.x, -self.y)