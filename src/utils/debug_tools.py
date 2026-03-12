import pygame

def draw_mouse_crosshair(screen, mouse_pos, width, height, color=(255, 0, 0)):
    mx, my = mouse_pos
    pygame.draw.line(screen, color, (mx, 0), (mx, height))
    pygame.draw.line(screen, color, (0, my), (width, my))

def draw_grid(screen, tile_size, width, height, color=(80, 80, 80)):
    for x in range(0, width, tile_size):
        pygame.draw.line(screen, color, (x, 0), (x, height))
    for y in range(0, height, tile_size):
        pygame.draw.line(screen, color, (0, y), (width, y))