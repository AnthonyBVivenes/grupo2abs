import pygame
from constants import CARD_WIDTH, CARD_HEIGHT, SYMBOL_SIZE, WHITE, BLACK

class Card:
    def __init__(self, card_id, symbols):
        self.id = card_id
        self.symbols = symbols
        self.image = None
        self.rect = None

    def draw(self, surface, x, y, highlight=False):
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
        pygame.draw.rect(surface, WHITE, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)
        if highlight:
            pygame.draw.rect(surface, (0, 255, 0), rect, 4)

        colors = [RED, BLUE, GREEN, (255, 255, 0), (255, 0, 255), (0, 255, 255), (128, 128, 128), (0, 128, 128)]
        spacing = CARD_WIDTH // (SYMBOLS_PER_CARD // 2 + 1)
        offset_x = 20
        offset_y = 20
        for i, sym in enumerate(self.symbols):
            col = i % 4
            row = i // 4
            cx = x + offset_x + col * spacing
            cy = y + offset_y + row * spacing
            pygame.draw.circle(surface, colors[i % len(colors)], (cx, cy), SYMBOL_SIZE // 2)
        self.rect = rect