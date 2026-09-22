#!/usr/bin/env python3
"""Genera imagen de dos cartas con símbolo coincidente MUY resaltado, fondo transparente."""
import pygame
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deck import Deck
from card import Card
from constants import (
    ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT, ASSET_SYMBOL_SIZE,
    GOLD, ACCENT_SUCCESS, WHITE, BLACK
)

def main():
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    # Configurar tamaño de carta en alta resolución
    Card.set_card_size(ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT)
    Card.set_layout(
        offset_x=40,
        offset_y=40,
        spacing=ASSET_CARD_WIDTH // 4,
        symbol_size=ASSET_SYMBOL_SIZE
    )
    
    # Generar mazo y encontrar un par de cartas con símbolo en común
    deck = Deck()
    card1 = deck.cards[0]
    card2 = deck.cards[1]
    
    # Encontrar el símbolo común
    common = set(card1.symbols) & set(card2.symbols)
    common_sym = list(common)[0]
    
    # Cargar symbol_map
    Card._load_symbol_map()
    
    print(f"Carta 0 y Carta 1 comparten el símbolo ID: {common_sym}")
    print(f"Archivo del sprite: {Card._symbol_map.get(str(common_sym))}")
    
    # Crear surface CON FONDO TRANSPARENTE (SRCALPHA)
    margin = 40
    gap = 100
    total_w = 2 * ASSET_CARD_WIDTH + gap + 2 * margin
    total_h = ASSET_CARD_HEIGHT + 2 * margin + 100
    
    surface = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    # NO rellenar fondo - queda transparente
    
    # Dibujar carta 1
    x1 = margin
    y1 = margin + 50
    card1_surf = card1.to_surface()
    surface.blit(card1_surf, (x1, y1))
    
    # Dibujar carta 2
    x2 = margin + ASSET_CARD_WIDTH + gap
    y2 = margin + 50
    card2_surf = card2.to_surface()
    surface.blit(card2_surf, (x2, y2))
    
    # Encontrar posiciones del símbolo común en ambas cartas
    layout = Card._layout_params
    cw, ch = ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT
    spacing = layout['spacing'] if layout['spacing'] is not None else cw // 4
    symbol_size = layout['symbol_size']
    row_spacing = symbol_size + 10
    
    card_center_x1 = x1 + cw // 2
    card_center_y1 = y1 + ch // 2
    card_center_x2 = x2 + cw // 2
    card_center_y2 = y2 + ch // 2
    
    positions1 = [
        (card_center_x1 - spacing, card_center_y1 - row_spacing),
        (card_center_x1, card_center_y1 - row_spacing),
        (card_center_x1 + spacing, card_center_y1 - row_spacing),
        (card_center_x1 - spacing // 2, card_center_y1),
        (card_center_x1 + spacing // 2, card_center_y1),
        (card_center_x1 - spacing, card_center_y1 + row_spacing),
        (card_center_x1, card_center_y1 + row_spacing),
        (card_center_x1 + spacing, card_center_y1 + row_spacing),
    ]
    
    positions2 = [
        (card_center_x2 - spacing, card_center_y2 - row_spacing),
        (card_center_x2, card_center_y2 - row_spacing),
        (card_center_x2 + spacing, card_center_y2 - row_spacing),
        (card_center_x2 - spacing // 2, card_center_y2),
        (card_center_x2 + spacing // 2, card_center_y2),
        (card_center_x2 - spacing, card_center_y2 + row_spacing),
        (card_center_x2, card_center_y2 + row_spacing),
        (card_center_x2 + spacing, card_center_y2 + row_spacing),
    ]
    
    # ===== RESALTADO MUY LLAMATIVO DEL SÍMBOLO COMÚN =====
    for i, sym in enumerate(card1.symbols):
        if sym == common_sym:
            cx, cy = positions1[i]
            highlight_symbol(surface, cx, cy, symbol_size)
    
    for i, sym in enumerate(card2.symbols):
        if sym == common_sym:
            cx, cy = positions2[i]
            highlight_symbol(surface, cx, cy, symbol_size)
    
    # Línea conectando ambos símbolos con efecto "brillo"
    pos1 = None
    pos2 = None
    for i, sym in enumerate(card1.symbols):
        if sym == common_sym:
            pos1 = positions1[i]
    for i, sym in enumerate(card2.symbols):
        if sym == common_sym:
            pos2 = positions2[i]
    
    if pos1 and pos2:
        draw_connection_line(surface, pos1, pos2)
    
    # Texto "¡COINCIDENCIA!" grande en el centro
    draw_match_text(surface, total_w // 2, (y1 + y2) // 2 + ch // 2 + 30)
    
    # Guardar
    output_dir = os.path.join(os.path.dirname(__file__), 'card_images')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'match_example_transparent.png')
    pygame.image.save(surface, output_path)
    print(f"\nGuardado: {output_path}")
    
    # También copiar a Pictures
    pictures_dir = os.path.expanduser('~/Pictures/Dobble_Tripticp')
    os.makedirs(pictures_dir, exist_ok=True)
    pictures_path = os.path.join(pictures_dir, 'match_example_transparent.png')
    pygame.image.save(surface, pictures_path)
    print(f"Copiado a: {pictures_path}")
    
    pygame.quit()


def highlight_symbol(surface, cx, cy, symbol_size):
    """Dibuja un resaltado MUY llamativo alrededor del símbolo."""
    base_r = symbol_size // 2
    
    # 1. Anillo exterior grueso y brillante (dorado)
    pygame.draw.circle(surface, (255, 215, 0), (cx, cy), base_r + 16, 8)
    
    # 2. Anillo medio naranja brillante
    pygame.draw.circle(surface, (255, 165, 0), (cx, cy), base_r + 12, 6)
    
    # 3. Anillo interior amarillo muy brillante
    pygame.draw.circle(surface, (255, 255, 0), (cx, cy), base_r + 8, 4)
    
    # 4. Anillo blanco casi en el borde del símbolo
    pygame.draw.circle(surface, (255, 255, 255, 200), (cx, cy), base_r + 4, 3)
    
    # 5. Efecto "pulso" - 4 líneas radiales brillantes
    for angle in [0, 45, 90, 135]:
        import math
        rad = math.radians(angle)
        x1 = cx + int((base_r + 20) * math.cos(rad))
        y1 = cy + int((base_r + 20) * math.sin(rad))
        x2 = cx + int((base_r + 40) * math.cos(rad))
        y2 = cy + int((base_r + 40) * math.sin(rad))
        pygame.draw.line(surface, (255, 255, 100), (x1, y1), (x2, y2), 4)
    
    # 6. Destellos en las esquinas (estrellitas)
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        sx = cx + dx * (base_r + 30)
        sy = cy + dy * (base_r + 30)
        draw_sparkle(surface, sx, sy, (255, 255, 150))


def draw_sparkle(surface, x, y, color):
    """Dibuja una pequeña estrella/destello."""
    size = 12
    # Cruz
    pygame.draw.line(surface, color, (x - size, y), (x + size, y), 3)
    pygame.draw.line(surface, color, (x, y - size), (x, y + size), 3)
    # Diagonales
    pygame.draw.line(surface, color, (x - size//2, y - size//2), (x + size//2, y + size//2), 2)
    pygame.draw.line(surface, color, (x - size//2, y + size//2), (x + size//2, y - size//2), 2)


def draw_connection_line(surface, pos1, pos2):
    """Dibuja una línea de conexión espectacular entre los dos símbolos."""
    x1, y1 = pos1
    x2, y2 = pos2
    
    # Línea principal gruesa con gradiente simulado (varias líneas)
    for i, color in enumerate([
        (255, 215, 0),    # Dorado
        (255, 200, 0),    # Naranja dorado
        (255, 230, 50),   # Amarillo
        (255, 255, 100),  # Amarillo claro
    ]):
        offset = i * 2
        pygame.draw.line(surface, color, 
                        (x1, y1 + offset), (x2, y2 + offset), 6 - i)
        pygame.draw.line(surface, color, 
                        (x1, y1 - offset), (x2, y2 - offset), 6 - i)
    
    # Línea central blanca muy brillante
    pygame.draw.line(surface, (255, 255, 255, 255), (x1, y1), (x2, y2), 3)
    
    # Flechas bidireccionales a lo largo de la línea
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2
    
    # Flecha hacia la derecha
    draw_arrow(surface, mid_x - 60, mid_y, 1, (255, 255, 100))
    # Flecha hacia la izquierda
    draw_arrow(surface, mid_x + 60, mid_y, -1, (255, 255, 100))
    
    # Texto "MATCH" en el centro de la línea
    font = pygame.font.Font(None, 56)
    text = font.render("MATCH", True, (255, 215, 0))
    # Sombra
    shadow = font.render("MATCH", True, (0, 0, 0, 180))
    surface.blit(shadow, (mid_x - text.get_width() // 2 + 3, mid_y - text.get_height() // 2 - 40 + 3))
    surface.blit(text, (mid_x - text.get_width() // 2, mid_y - text.get_height() // 2 - 40))


def draw_arrow(surface, x, y, direction, color):
    """Dibuja una flecha triangular."""
    size = 18
    if direction > 0:
        # Flecha hacia la derecha
        points = [
            (x, y),
            (x - size, y - size // 2),
            (x - size, y + size // 2),
        ]
    else:
        # Flecha hacia la izquierda
        points = [
            (x, y),
            (x + size, y - size // 2),
            (x + size, y + size // 2),
        ]
    pygame.draw.polygon(surface, color, points)


def draw_match_text(surface, cx, cy):
    """Dibuja el texto principal '¡COINCIDENCIA!' con efecto."""
    font = pygame.font.Font(None, 72)
    text = "¡COINCIDENCIA!"
    
    # Sombra proyectada
    shadow = font.render(text, True, (0, 0, 0, 200))
    # Texto principal dorado
    main = font.render(text, True, (255, 215, 0))
    # Borde blanco
    outline = font.render(text, True, (255, 255, 255))
    
    # Dibujar múltiples capas para efecto 3D
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        surface.blit(outline, (cx - outline.get_width() // 2 + dx, cy - outline.get_height() // 2 + dy))
    surface.blit(shadow, (cx - shadow.get_width() // 2 + 4, cy - shadow.get_height() // 2 + 4))
    surface.blit(main, (cx - main.get_width() // 2, cy - main.get_height() // 2))
    
    # Subtexto
    font_small = pygame.font.Font(None, 36)
    sub = font_small.render("Mismo símbolo en ambas cartas", True, (255, 230, 100))
    surface.blit(sub, (cx - sub.get_width() // 2, cy + 40))


if __name__ == '__main__':
    main()