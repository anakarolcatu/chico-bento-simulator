import pygame
from settings import FONT_PATH


class FontManager:

    _cache = {}

    @classmethod
    def get(cls, size):
        if size not in cls._cache:
            cls._cache[size] = pygame.font.Font(FONT_PATH, size)

        return cls._cache[size]