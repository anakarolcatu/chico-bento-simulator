import pygame
from src.utils.spritesheet import get_sprite
from src.utils.ui_helper import nine_slice
from src.data.crops import CROPS
from src.utils.asset_loader import AssetLoader


class ShopOverlay:
    def __init__(self, inventory, font, title_font=None, audio=None):
        self.inventory = inventory
        self.font = font
        self.title_font = title_font or font
        self.audio = audio

        self.is_open = False
        self.active_panel = "buy"
        self.selected_buy_index = 0
        self.selected_sell_index = 0

        # preços de compra das sementes
        self.buy_seed_prices = {
            seed_name: crop_data["sell_price"] // 2 + 1
            for seed_name, crop_data in CROPS.items()
        }

        self.buy_items = list(CROPS.keys())

        sheet = AssetLoader.load_image("assets/ui/Shop.png")

        # recortes base
        panel_base = get_sprite(sheet, 7, 0, 115, 149)
        self.slot_img = get_sprite(sheet, 356, 160, 23, 23)
        self.slot_img = pygame.transform.scale(self.slot_img, (54, 54))

        self.coin_img = get_sprite(sheet, 483, 163, 11, 11)
        self.coin_img = pygame.transform.scale(self.coin_img, (18, 18))

        # painéis
        self.left_panel = nine_slice(panel_base, 320, 380, 4)
        self.right_panel = nine_slice(panel_base, 320, 380, 4)

        self.left_rect = self.left_panel.get_rect(center=(360, 260))
        self.right_rect = self.right_panel.get_rect(center=(820, 260))

        # ícones de sementes e plantas
        self.item_icons = AssetLoader.load_crop_icons((26, 26))

        self.header_offset_y = 16

        self.grid_cols = 3
        self.grid_start_x = 38
        self.grid_start_y = 72
        self.grid_spacing_x = 32
        self.grid_spacing_y = 16

        self.slot_price_offset_y = 10
        self.slot_stack_padding_x = 3
        self.slot_stack_padding_y = 1

        self.footer_info_offset_y = 38

        self.money_offset_x = 24
        self.money_offset_y = 54
        self.money_gap = 6

        self.help_text_y = 460

    def open(self):
        self.is_open = True
        self.active_panel = "buy"

    def close(self):
        self.is_open = False

    def get_crop_color_from_crop_name(self, crop_name):
        for seed_name, crop_data in CROPS.items():
            if crop_data["crop_name"] == crop_name:
                return crop_data["color"]
        return (40, 170, 40)

    def get_sell_price(self, crop_name):
        for seed_name, crop_data in CROPS.items():
            if crop_data["crop_name"] == crop_name:
                return crop_data["sell_price"]
        return 0

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

    def move_grid_selection(self, current_index, key, total_items):
        cols = self.grid_cols

        if total_items == 0:
            return 0

        row = current_index // cols
        col = current_index % cols

        max_row = (total_items - 1) // cols

        if key == pygame.K_LEFT:
            if col > 0:
                current_index -= 1

        elif key == pygame.K_RIGHT:
            if col < cols - 1 and current_index + 1 < total_items:
                current_index += 1

        elif key == pygame.K_UP:
            if row > 0:
                current_index -= cols

        elif key == pygame.K_DOWN:
            if row < max_row and current_index + cols < total_items:
                current_index += cols

        return current_index


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

            if self.audio:
                self.audio.play_sound("menu_select")
            return money

        if self.active_panel == "buy":
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                self.selected_buy_index = self.move_grid_selection(
                    self.selected_buy_index,
                    event.key,
                    len(self.buy_items)
                )
                if self.audio:
                    self.audio.play_sound("menu_select")
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                seed_name = self.buy_items[self.selected_buy_index]
                price = self.buy_seed_prices[seed_name]

                if money >= price:
                    added = self.inventory.add_item(seed_name, 1)
                    if added:
                        money -= price
                        if self.audio:
                            self.audio.play_sound("money")

        elif self.active_panel == "sell":
            sell_items = self.get_sell_items()

            if sell_items:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    self.selected_sell_index = self.move_grid_selection(
                        self.selected_sell_index,
                        event.key,
                        len(sell_items)
                    )   
                    if self.audio:
                        self.audio.play_sound("menu_select")
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    crop_name = sell_items[self.selected_sell_index]
                    sell_price = self.get_sell_price(crop_name)

                    amount = self.inventory.remove_all(crop_name)
                    if amount > 0:
                        money += amount * sell_price
                        if self.audio:
                            self.audio.play_sound("money")

                    sell_items = self.get_sell_items()
                    if sell_items:
                        self.selected_sell_index = min(self.selected_sell_index, len(sell_items) - 1)
                    else:
                        self.selected_sell_index = 0
        return money

    # Desenho
    def draw_item_grid(self, screen, panel_rect, items, selected_index, active, mode="buy"):
        for i, item in enumerate(items):
            row = i // self.grid_cols
            col = i % self.grid_cols

            x = panel_rect.x + self.grid_start_x + col * (48 + self.grid_spacing_x)
            y = panel_rect.y + self.grid_start_y + row * (48 + self.grid_spacing_y + 22)

            slot_rect = self.slot_img.get_rect(topleft=(x, y))
            screen.blit(self.slot_img, slot_rect)

            if active and i == selected_index:
                pygame.draw.rect(screen, (255, 230, 120), slot_rect, 3, border_radius=4)

            if mode == "buy":
                if mode == "buy":
                    drawn = self.draw_item_icon(screen, item, slot_rect)

                    if not drawn:
                        color = CROPS[item]["color"]
                        pygame.draw.circle(screen, color, slot_rect.center, 8)

                    price = self.buy_seed_prices[item]
                    price_surface = self.font.render(str(price), False, (20, 20, 20))

                    text_rect = price_surface.get_rect(
                        center=(slot_rect.centerx - 6, slot_rect.bottom + self.slot_price_offset_y)
                    )
                    coin_rect = self.coin_img.get_rect(
                        midleft=(text_rect.right + 2, text_rect.centery)
                    )

                    screen.blit(price_surface, text_rect)
                    screen.blit(self.coin_img, coin_rect)

            elif mode == "sell":
                drawn = self.draw_item_icon(screen, item, slot_rect)

                if not drawn:
                    color = self.get_crop_color_from_crop_name(item)
                    pygame.draw.circle(screen, color, slot_rect.center, 10)

                amount = self.inventory.get_amount(item)
                amount_text = self.font.render(str(amount), False, (20, 20, 20))
                amount_rect = amount_text.get_rect(
                    bottomright=(
                        slot_rect.right - self.slot_stack_padding_x,
                        slot_rect.bottom - self.slot_stack_padding_y
                    )
                )
                screen.blit(amount_text, amount_rect)

                sell_price = self.get_sell_price(item)
                price_surface = self.font.render(str(sell_price), False, (20, 20, 20))

                text_rect = price_surface.get_rect(
                    center=(slot_rect.centerx - 6, slot_rect.bottom + self.slot_price_offset_y)
                )
                coin_rect = self.coin_img.get_rect(
                    midleft=(text_rect.right + 2, text_rect.centery)
                )

                screen.blit(price_surface, text_rect)
                screen.blit(self.coin_img, coin_rect)

    def draw_item_icon(self, screen, item_name, slot_rect):
        icon = self.item_icons.get(item_name)

        if icon is None:
            return False

        icon_rect = icon.get_rect(center=slot_rect.center)
        screen.blit(icon, icon_rect)
        return True

    def draw_selected_item_info(self, screen, panel_rect, item_name, mode="buy"):
        info_y = panel_rect.bottom - self.footer_info_offset_y

        if mode == "buy":
            crop_data = CROPS[item_name]
            text = crop_data["crop_name"].replace("_", " ").title()

        else:
            crop_name = item_name.replace("_", " ").title()
            amount = self.inventory.get_amount(item_name)
            text = f"{crop_name} x{amount}"

        info_surface = self.font.render(text, False, (20, 20, 20))
        info_rect = info_surface.get_rect(center=(panel_rect.centerx, info_y))
        screen.blit(info_surface, info_rect)

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
            screen.blit(
                empty_text,
                empty_text.get_rect(center=(self.right_rect.centerx, self.right_rect.centery))
            )
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

    def draw_money_info(self, screen, money):
        money_surface = self.font.render(str(money), False, (20, 20, 20))

        coin_rect = self.coin_img.get_rect(
            midleft=(
                self.left_rect.x + self.money_offset_x,
                self.left_rect.y + self.money_offset_y
            )
        )

        money_rect = money_surface.get_rect(
            midleft=(coin_rect.right + self.money_gap, coin_rect.centery)
        )

        screen.blit(self.coin_img, coin_rect)
        screen.blit(money_surface, money_rect)
    
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

        screen.blit(
            buy_title,
            buy_title.get_rect(center=(self.left_rect.centerx, self.left_rect.y + self.header_offset_y))
        )
        screen.blit(
            sell_title,
            sell_title.get_rect(center=(self.right_rect.centerx, self.right_rect.y + self.header_offset_y))
        )

        self.draw_money_info(screen, money)

        help_text = self.font.render("TAB alterna | ENTER confirma | ESC fecha", False, (20, 20, 20))
        screen.blit(help_text, help_text.get_rect(center=(screen.get_width() // 2, self.help_text_y)))

        self.draw_buy_list(screen)
        self.draw_sell_list(screen)