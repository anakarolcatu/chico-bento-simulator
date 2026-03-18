import pygame
from src.utils.spritesheet import get_sprite
from src.data.crops import CROPS

class AssetLoader:
    _images = {}
    _icons = {}

    @staticmethod
    def load_image(path):
        if path not in AssetLoader._images:
            try:
                AssetLoader._images[path] = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"Erro ao carregar imagem {path}: {e}")
                return None
        return AssetLoader._images[path]
    
    @staticmethod
    def load_crop_icons(scale_size=(24, 24)):
        # Cache por tamanho para evitar processamento repetido
        scale_key = f"{scale_size[0]}x{scale_size[1]}"
        
        if scale_key in AssetLoader._icons:
             return AssetLoader._icons[scale_key]

        icons = {}
        
        for seed_name, crop_data in CROPS.items():
            # ícone da semente
            if "seed_sheet" in crop_data and "seed_icon" in crop_data:
                seed_sheet = AssetLoader.load_image(crop_data["seed_sheet"])
                if seed_sheet:
                    x, y, w, h = crop_data["seed_icon"]
                    icon = get_sprite(seed_sheet, x, y, w, h)
                    icon = pygame.transform.scale(icon, scale_size)
                    icons[seed_name] = icon

            # ícone da colheita
            if "crop_sheet" in crop_data and "crop_icon" in crop_data:
                crop_sheet = AssetLoader.load_image(crop_data["crop_sheet"])
                if crop_sheet:
                    x, y, w, h = crop_data["crop_icon"]
                    icon = get_sprite(crop_sheet, x, y, w, h)
                    icon = pygame.transform.scale(icon, scale_size)
                    icons[crop_data["crop_name"]] = icon
        
        AssetLoader._icons[scale_key] = icons
        return icons
