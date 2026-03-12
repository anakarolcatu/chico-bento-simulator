import os
import sys
import pygame

# Permite importar módulos do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

pygame.init()

IMAGE_PATH = "assets/ui/Settings.png"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
BG_COLOR = (30, 30, 30)
GRID_COLOR = (70, 70, 70)
CROSSHAIR_COLOR = (255, 0, 0)
SELECTION_COLOR = (0, 255, 0)
TEXT_COLOR = (255, 255, 255)
INFO_BG = (0, 0, 0)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Sprite Inspector")

clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 20)

sheet = pygame.image.load(IMAGE_PATH).convert_alpha()

zoom = 2
grid_size = 16
offset_x = 20
offset_y = 20

dragging = False
start_pos = None
end_pos = None


def draw_grid(surface, img_rect, cell_size, color):
    for x in range(img_rect.left, img_rect.right + 1, cell_size):
        pygame.draw.line(surface, color, (x, img_rect.top), (x, img_rect.bottom))
    for y in range(img_rect.top, img_rect.bottom + 1, cell_size):
        pygame.draw.line(surface, color, (img_rect.left, y), (img_rect.right, y))


def screen_to_image(mouse_pos):
    mx, my = mouse_pos
    img_x = (mx - offset_x) // zoom
    img_y = (my - offset_y) // zoom
    return int(img_x), int(img_y)


def clamp_to_image(x, y):
    x = max(0, min(x, sheet.get_width() - 1))
    y = max(0, min(y, sheet.get_height() - 1))
    return x, y


def normalize_rect(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    left = min(x1, x2)
    top = min(y1, y2)
    right = max(x1, x2)
    bottom = max(y1, y2)

    width = right - left + 1
    height = bottom - top + 1

    return left, top, width, height


def draw_text_block(lines, x, y):
    padding = 8
    rendered = [font.render(line, True, TEXT_COLOR) for line in lines]
    width = max(text.get_width() for text in rendered) + padding * 2
    height = sum(text.get_height() for text in rendered) + padding * 2 + 4 * (len(rendered) - 1)

    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, INFO_BG, bg_rect)
    pygame.draw.rect(screen, (180, 180, 180), bg_rect, 1)

    current_y = y + padding
    for text in rendered:
        screen.blit(text, (x + padding, current_y))
        current_y += text.get_height() + 4


def save_selection_preview(x, y, w, h):
    preview = pygame.Surface((w, h), pygame.SRCALPHA)
    preview.blit(sheet, (0, 0), (x, y, w, h))
    pygame.image.save(preview, "selection_preview.png")


running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                zoom = min(zoom + 1, 16)

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                zoom = max(1, zoom - 1)

            elif event.key == pygame.K_LEFTBRACKET:
                grid_size = max(1, grid_size - 1)

            elif event.key == pygame.K_RIGHTBRACKET:
                grid_size += 1

            elif event.key == pygame.K_s and start_pos and end_pos:
                x, y, w, h = normalize_rect(start_pos, end_pos)
                save_selection_preview(x, y, w, h)
                print(f"Preview salvo: x={x}, y={y}, w={w}, h={h}")

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                img_x, img_y = screen_to_image(event.pos)
                img_x, img_y = clamp_to_image(img_x, img_y)
                start_pos = (img_x, img_y)
                end_pos = (img_x, img_y)
                dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging:
                img_x, img_y = screen_to_image(event.pos)
                img_x, img_y = clamp_to_image(img_x, img_y)
                end_pos = (img_x, img_y)
                dragging = False

                x, y, w, h = normalize_rect(start_pos, end_pos)
                print(f"x={x}, y={y}, w={w}, h={h}")

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                img_x, img_y = screen_to_image(event.pos)
                img_x, img_y = clamp_to_image(img_x, img_y)
                end_pos = (img_x, img_y)

    scaled_sheet = pygame.transform.scale(
        sheet,
        (sheet.get_width() * zoom, sheet.get_height() * zoom)
    )

    screen.fill(BG_COLOR)
    screen.blit(scaled_sheet, (offset_x, offset_y))

    image_rect = pygame.Rect(
        offset_x,
        offset_y,
        scaled_sheet.get_width(),
        scaled_sheet.get_height()
    )

    draw_grid(screen, image_rect, grid_size * zoom, GRID_COLOR)

    mx, my = mouse_pos
    if image_rect.collidepoint(mouse_pos):
        pygame.draw.line(screen, CROSSHAIR_COLOR, (mx, image_rect.top), (mx, image_rect.bottom))
        pygame.draw.line(screen, CROSSHAIR_COLOR, (image_rect.left, my), (image_rect.right, my))

    img_mouse_x, img_mouse_y = screen_to_image(mouse_pos)
    img_mouse_x, img_mouse_y = clamp_to_image(img_mouse_x, img_mouse_y)

    info_lines = [
        f"arquivo: {IMAGE_PATH}",
        f"mouse img: x={img_mouse_x}, y={img_mouse_y}",
        f"zoom: {zoom}x",
        f"grid: {grid_size}px",
        "arraste com botão esquerdo para selecionar",
        "teclas: +/- zoom | [ ] grid | S salva preview | ESC sai",
    ]

    if start_pos and end_pos:
        x, y, w, h = normalize_rect(start_pos, end_pos)
        info_lines.extend([
            f"seleção: x={x}, y={y}, w={w}, h={h}",
            f"get_sprite(sheet, {x}, {y}, {w}, {h})"
        ])

        sel_rect = pygame.Rect(
            offset_x + x * zoom,
            offset_y + y * zoom,
            w * zoom,
            h * zoom
        )
        pygame.draw.rect(screen, SELECTION_COLOR, sel_rect, 2)

    draw_text_block(info_lines, 20, WINDOW_HEIGHT - 180)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()