import pygame
from src.utils.spritesheet import get_sprite
from src.utils.ui_helper import nine_slice
from src.data.crops import CROPS

class ShopOverlay:
    def __init__(self, inventory, font, title_font=None):
        self.inventory = inventory
        self.font = font
        self.title_font = title_font or font

        self.is_open = False
        self.active_panel = "buy"  
        self.selected_buy_index = 0
        self.selected_sell_index = 0

        self.buy_seed_prices = {
            seed_name: crop_data["sell_price"] // 2 + 1
            for seed_name, crop_data in CROPS.items()
        }

        self.buy_items = list(CROPS.keys())

        sheet = pygame.image.load("assets/ui/Shop.png").convert_alpha()
        panel_base = get_sprite(sheet, 7, 0, 115, 149)
        self.slot_img = get_sprite(sheet, 356, 160, 23, 23)
        self.slot_img = pygame.transform.scale(self.slot_img, (54, 54))

        # painéis base
        self.left_panel = nine_slice(panel_base, 320, 380, 4)
        self.right_panel = nine_slice(panel_base, 320, 380, 4)

        self.left_rect = self.left_panel.get_rect(center=(360, 260))
        self.right_rect = self.right_panel.get_rect(center=(820, 260))

        self.item_spacing = 40
        self.item_start_y = 120

    def draw_item_grid(self, screen, panel_rect, items, selected_index, active, mode="buy"):
        cols = 3
        spacing_x = 32
        spacing_y = 16
        start_x = panel_rect.x + 38
        start_y = panel_rect.y + 72

        for i, item in enumerate(items):
            row = i // cols
            col = i % cols

            x = start_x + col * (48 + spacing_x)
            y = start_y + row * (48 + spacing_y + 22)

            slot_rect = self.slot_img.get_rect(topleft=(x, y))
            screen.blit(self.slot_img, slot_rect)

            if active and i == selected_index:
                pygame.draw.rect(screen, (255, 230, 120), slot_rect, 3, border_radius=4)

            if mode == "buy":
                color = CROPS[item]["color"]
                pygame.draw.circle(screen, color, slot_rect.center, 8)
                price = self.buy_seed_prices[item]
                price_text = self.font.render(f"${price}", False, (20, 20, 20))
                price_rect = price_text.get_rect(center=(slot_rect.centerx, slot_rect.bottom + 10))
                screen.blit(price_text, price_rect)


            elif mode == "sell":
                color = (40, 170, 40)
                pygame.draw.circle(screen, color, slot_rect.center, 10)

                amount = self.inventory.get_amount(item)
                amount_text = self.font.render(str(amount), False, (20, 20, 20))
                text_rect = amount_text.get_rect(bottomright=(slot_rect.right - 3, slot_rect.bottom - 1))
                screen.blit(amount_text, text_rect)
                sell_price = 0
                for seed_name, crop_data in CROPS.items():
                    if crop_data["crop_name"] == item:
                        sell_price = crop_data["sell_price"]
                        break

                price_text = self.font.render(f"${sell_price}", False, (20, 20, 20))
                price_rect = price_text.get_rect(center=(slot_rect.centerx, slot_rect.bottom + 10))
                screen.blit(price_text, price_rect)

    def draw_selected_item_info(self, screen, panel_rect, item_name, mode="buy"):
        info_y = panel_rect.bottom - 55

        if mode == "buy":
            crop_data = CROPS[item_name]
            item_label = crop_data["crop_name"].replace("_", " ").title()
            price = self.buy_seed_prices[item_name]
            text = f"{item_label}"

        else:
            crop_name = item_name.replace("_", " ").title()
            amount = self.inventory.get_amount(item_name)

            sell_price = 0
            for seed_name, crop_data in CROPS.items():
                if crop_data["crop_name"] == item_name:
                    sell_price = crop_data["sell_price"]
                    break

            text = f"{crop_name} x{amount} - ${sell_price}"

        info_surface = self.font.render(text, False, (20, 20, 20))
        info_rect = info_surface.get_rect(center=(panel_rect.centerx, info_y))
        screen.blit(info_surface, info_rect)

    def open(self):
        self.is_open = True
        self.active_panel = "buy"

    def close(self):
        self.is_open = False

    def get_sell_items(self):
        sell_items = []

        crop_names = {crop_data["crop_name"] for crop_data in CROPS.values()}

        for i in range(self.inventory.size):
            slot = self.inventory.get_slot(i)
            if slot is not None and slot["item"] in crop_names:
                sell_items.append(slot["item"])

        unique_items = []
        seen = set()

        for item in sell_items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)

        return unique_items

    def get_buy_label(self, seed_name):
        crop_data = CROPS[seed_name]
        crop_name = crop_data["crop_name"].replace("_", " ").title()
        price = self.buy_seed_prices[seed_name]
        return f"{crop_name} - ${price}"

    def get_sell_label(self, crop_name):
        crop_display = crop_name.replace("_", " ").title()

        sell_price = 0
        for seed_name, crop_data in CROPS.items():
            if crop_data["crop_name"] == crop_name:
                sell_price = crop_data["sell_price"]
                break

        amount = self.inventory.get_amount(crop_name)

        return f"{crop_display} x{amount} - ${sell_price}"

    def handle_event(self, event, money):
        if event.type != pygame.KEYDOWN:
            return money

        if event.key == pygame.K_ESCAPE:
            self.close()
            return money

        if event.key == pygame.K_TAB:
            if self.active_panel == "buy":
                self.active_panel = "sell"
            else:
                self.active_panel = "buy"
            return money

        if self.active_panel == "buy":
            if event.key == pygame.K_UP:
                self.selected_buy_index = (self.selected_buy_index - 1) % len(self.buy_items)

            elif event.key == pygame.K_DOWN:
                self.selected_buy_index = (self.selected_buy_index + 1) % len(self.buy_items)

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                seed_name = self.buy_items[self.selected_buy_index]
                price = self.buy_seed_prices[seed_name]

                if money >= price:
                    added = self.inventory.add_item(seed_name, 1)
                    if added:
                        money -= price

        elif self.active_panel == "sell":
            sell_items = self.get_sell_items()

            if sell_items:
                if event.key == pygame.K_UP:
                    self.selected_sell_index = (self.selected_sell_index - 1) % len(sell_items)

                elif event.key == pygame.K_DOWN:
                    self.selected_sell_index = (self.selected_sell_index + 1) % len(sell_items)

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    crop_name = sell_items[self.selected_sell_index]

                    sell_price = 0
                    for seed_name, crop_data in CROPS.items():
                        if crop_data["crop_name"] == crop_name:
                            sell_price = crop_data["sell_price"]
                            break

                    amount = self.inventory.remove_all(crop_name)
                    if amount > 0:
                        money += amount * sell_price

                    sell_items = self.get_sell_items()
                    if sell_items:
                        self.selected_sell_index %= len(sell_items)
                    else:
                        self.selected_sell_index = 0

        return money

    def draw(self, screen, money):
        if not self.is_open:
            return

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        screen.blit(self.left_panel, self.left_rect)
        screen.blit(self.right_panel, self.right_rect)

        buy_title = self.title_font.render("COMPRAR", False, (20, 20, 20))
        sell_title = self.title_font.render("VENDER", False, (20, 20, 20))

        screen.blit(buy_title, buy_title.get_rect(center=(self.left_rect.centerx, self.left_rect.y + 16)))
        screen.blit(sell_title, sell_title.get_rect(center=(self.right_rect.centerx, self.right_rect.y + 16)))

        money_text = self.font.render(f"Dinheiro: ${money}", False, (20, 20, 20))
        screen.blit(money_text, money_text.get_rect(center=(screen.get_width() // 2, 430)))

        help_text = self.font.render("TAB alterna | ENTER confirma | ESC fecha", False, (20, 20, 20))
        screen.blit(help_text, help_text.get_rect(center=(screen.get_width() // 2, 460)))

        self.draw_buy_list(screen)
        self.draw_sell_list(screen)

    def draw_buy_list(self, screen):
        self.draw_item_grid(
        screen,
        self.left_rect,
        self.buy_items,
        self.selected_buy_index,
        self.active_panel == "buy",
        mode="buy"
        )

        if self.buy_items:
            selected_item = self.buy_items[self.selected_buy_index]
            self.draw_selected_item_info(screen, self.left_rect, selected_item, mode="buy")

    def draw_sell_list(self, screen):
        sell_items = self.get_sell_items()

        if not sell_items:
            empty_text = self.font.render("Nada para vender", False, (20, 20, 20))
            screen.blit(empty_text, empty_text.get_rect(center=(self.right_rect.centerx, self.right_rect.centery)))
            return

        self.draw_item_grid(
            screen,
            self.right_rect,
            sell_items,
            self.selected_sell_index,
            self.active_panel == "sell",
            mode="sell"
        )

        selected_item = sell_items[self.selected_sell_index]
        self.draw_selected_item_info(screen, self.right_rect, selected_item, mode="sell")