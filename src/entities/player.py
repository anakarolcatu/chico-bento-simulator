import pygame
from src.utils.spritesheet import get_sprite
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.speed = 220
        self.scale = 2

        self.frame_width = 64
        self.frame_height = 64

        self.sheet = pygame.image.load("assets/player/Unarmed_Walk_with_shadow.png").convert_alpha()

        self.animations = self.load_animations()

        self.direction = "down"
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12

        self.image = self.animations[self.direction][self.current_frame]
        self.rect = self.image.get_rect(center=(self.x, self.y))

        self.hitbox = pygame.Rect(0, 0, 24, 18)
        self.hitbox.center = (self.x, self.y + 18)

    def load_animations(self):
        animations = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }

        directions = ["down", "left", "right", "up"]

        for row, direction in enumerate(directions):
            for col in range(6):
                x = col * self.frame_width
                y = row * self.frame_height

                frame = get_sprite(
                    self.sheet,
                    x,
                    y,
                    self.frame_width,
                    self.frame_height
                )
                new_size = int(self.frame_width * self.scale)
                frame = pygame.transform.scale(frame, (new_size, new_size))

                animations[direction].append(frame)

        return animations

    def move_and_collide(self, dx, dy, obstacles):
        self.hitbox.x += dx
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                if dx > 0:
                    self.hitbox.right = obstacle.left
                elif dx < 0:
                    self.hitbox.left = obstacle.right

        self.hitbox.y += dy
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                if dy > 0:
                    self.hitbox.bottom = obstacle.top
                elif dy < 0:
                    self.hitbox.top = obstacle.bottom

        if self.hitbox.left < 0:
            self.hitbox.left = 0
        if self.hitbox.right > SCREEN_WIDTH:
            self.hitbox.right = SCREEN_WIDTH
        if self.hitbox.top < 0:
            self.hitbox.top = 0
        if self.hitbox.bottom > SCREEN_HEIGHT:
            self.hitbox.bottom = SCREEN_HEIGHT

        self.x = self.hitbox.centerx
        self.y = self.hitbox.centery - 18
        self.rect.center = (round(self.x), round(self.y))

    def update(self, dt, obstacles):
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0
        moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            self.direction = "right"
            moving = True

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
            self.direction = "up"
            moving = True
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            self.direction = "down"
            moving = True

        if dx != 0 and dy != 0:
            length = (dx ** 2 + dy ** 2) ** 0.5
            dx /= length
            dy /= length

        move_x = dx * self.speed * dt
        move_y = dy * self.speed * dt

        self.move_and_collide(move_x, move_y, obstacles)

        if moving:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.animations[self.direction])
        else:
            self.current_frame = 0

        self.image = self.animations[self.direction][self.current_frame]

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # debug hitbox
        # pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 1)