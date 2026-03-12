import pygame

class Button:
    def __init__(
        self,
        normal_image,
        selected_image,
        pressed_image,
        x,
        y,
        text,
        font,
        text_color,
        selected_text_color=None,
    ):
        self.normal_image = normal_image
        self.selected_image = selected_image
        self.pressed_image = pressed_image

        self.current_image = self.normal_image
        self.rect = self.current_image.get_rect(center=(x, y))

        self.text = text
        self.font = font
        self.text_color = text_color
        self.selected_text_color = selected_text_color or text_color

        self.state = "normal"

    def set_state(self, state):
        self.state = state

        if state == "normal":
            self.current_image = self.normal_image
        elif state == "selected":
            self.current_image = self.selected_image
        elif state == "pressed":
            self.current_image = self.pressed_image

    def draw(self, screen):
        screen.blit(self.current_image, self.rect)

        color = self.selected_text_color if self.state in ("selected", "pressed") else self.text_color

        text_surface = self.font.render(self.text, True, color)

        text_y_offset = 2 if self.state == "pressed" else -1
        text_rect = text_surface.get_rect(
            center=(self.rect.centerx, self.rect.centery + text_y_offset)
        )

        screen.blit(text_surface, text_rect)