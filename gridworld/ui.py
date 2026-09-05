import pygame

COL_BTN = (45, 50, 58)
COL_BTN_HOVER = (60, 66, 76)
COL_BTN_DISABLED = (35, 37, 42)
COL_BORDER = (90, 96, 108)
COL_TEXT = (240, 240, 240)
COL_TEXT_DISABLED = (110, 112, 118)


class Button:
    def __init__(self, rect: pygame.Rect, label: str, enabled: bool = True):
        self.rect = rect
        self.label = label
        self.enabled = enabled

    def is_clicked(self, pos) -> bool:
        return self.enabled and self.rect.collidepoint(pos)

    def draw(self, screen, font):
        hovering = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        if not self.enabled:
            color = COL_BTN_DISABLED
        elif hovering:
            color = COL_BTN_HOVER
        else:
            color = COL_BTN
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, COL_BORDER, self.rect, 2, border_radius=8)
        text_color = COL_TEXT if self.enabled else COL_TEXT_DISABLED
        text_surf = font.render(self.label, True, text_color)
        screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
