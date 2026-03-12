import pygame


def nine_slice(surface, target_width, target_height, border):
    sw, sh = surface.get_size()

    result = pygame.Surface((target_width, target_height), pygame.SRCALPHA)

    # cantos
    top_left = surface.subsurface((0, 0, border, border))
    top_right = surface.subsurface((sw - border, 0, border, border))
    bottom_left = surface.subsurface((0, sh - border, border, border))
    bottom_right = surface.subsurface((sw - border, sh - border, border, border))

    # bordas
    top = surface.subsurface((border, 0, sw - 2 * border, border))
    bottom = surface.subsurface((border, sh - border, sw - 2 * border, border))
    left = surface.subsurface((0, border, border, sh - 2 * border))
    right = surface.subsurface((sw - border, border, border, sh - 2 * border))

    # centro
    center = surface.subsurface((border, border, sw - 2 * border, sh - 2 * border))

    top = pygame.transform.scale(top, (target_width - 2 * border, border))
    bottom = pygame.transform.scale(bottom, (target_width - 2 * border, border))
    left = pygame.transform.scale(left, (border, target_height - 2 * border))
    right = pygame.transform.scale(right, (border, target_height - 2 * border))
    center = pygame.transform.scale(center, (target_width - 2 * border, target_height - 2 * border))

    result.blit(top_left, (0, 0))
    result.blit(top_right, (target_width - border, 0))
    result.blit(bottom_left, (0, target_height - border))
    result.blit(bottom_right, (target_width - border, target_height - border))

    result.blit(top, (border, 0))
    result.blit(bottom, (border, target_height - border))
    result.blit(left, (0, border))
    result.blit(right, (target_width - border, border))
    result.blit(center, (border, border))

    return result