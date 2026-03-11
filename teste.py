import os
import pygame

pygame.init()

print("cwd:", os.getcwd())
print("extended:", pygame.image.get_extended())

path = "assets/ui/main_menu_bg.png"
print("exists:", os.path.exists(path))
print("abs path:", os.path.abspath(path))

img = pygame.image.load(path)
print("loaded:", img.get_size())