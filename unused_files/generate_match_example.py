#!/usr/bin/env python3
"""Genera imagen de dos cartas con símbolo coincidente resaltado."""
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
    
    # Crear surface para ambas cartas lado a lado
    margin = 60
    gap = 80
    total_w = 2 * ASSET_CARD_WIDTH + gap + 2 * margin
    total_h = ASSET_CARD_HEIGHT + 2 * margin + 120  # espacio extra para título
    
    surface = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    surface.fill((25, 25, 35))
    
    # Título
    font_title = pygame.font.Font(None, 56)
    title = font_title.render("DOBBLE - Coincidencia Encontrada", True, GOLD)
    surface.blit(title, (total_w // 2 - title.get_width() // 2, 20))
    
    # Dibujar carta 1
    x1 = margin
    y1 = margin + 80
    card1_surf = card1.to_surface()
    surface.blit(card1_surf, (x1, y1))
    
    # Dibujar carta 2
    x2 = margin + ASSET_CARD_WIDTH + gap
    y2 = margin + 80
    card2_surf = card2.to_surface()
    surface.blit(card2_surf, (x2, y2))
    
    # Encontrar posiciones del símbolo común en ambas cartas
    # Recalcular posiciones igual que en Card.draw()
    layout = Card._layout_params
    cw, ch = ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT
    spacing = layout['spacing'] if layout['spacing'] is not None else cw // 4
    symbol_size = layout['symbol_size']
    row_spacing = symbol_size + 10
    
    card_center_x1 = x1 + cw // 2
    card_center_y1 = y1 + ch // 2
    card_center_x2 = x2 + cw // 2
    card_center_y2 = y2 + ch // 2
    
    positions = [
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
    
    # Resaltar símbolo común en ambas cartas con anillo dorado pulsante
    for i, sym in enumerate(card1.symbols):
        if sym == common_sym:
            cx, cy = positions[i]
            # Anillo exterior grueso
            pygame.draw.circle(surface, GOLD, (cx, cy), symbol_size // 2 + 8, 6)
            # Anillo interior brillante
            pygame.draw.circle(surface, (255, 255, 200), (cx, cy), symbol_size // 2 + 4, 3)
            # Pequeño indicador "¡MATCH!"
            font_match = pygame.font.Font(None, 36)
            match_text = font_match.render("¡MATCH!", True, GOLD)
            surface.blit(match_text, (cx - match_text.get_width() // 2, cy - symbol_size // 2 - 40))
    
    for i, sym in enumerate(card2.symbols):
        if sym == common_sym:
            cx, cy = positions2[i]
            pygame.draw.circle(surface, GOLD, (cx, cy), symbol_size // 2 + 8, 6)
            pygame.draw.circle(surface, (255, 255, 200), (cx, cy), symbol_size // 2 + 4, 3)
            font_match = pygame.font.Font(None, 36)
            match_text = font_match.render("¡MATCH!", True, GOLD)
            surface.blit(match_text, (cx - match_text.get_width() // 2, cy - symbol_size // 2 - 40))
    
    # Línea conectando ambos símbolos
    # Encontrar posiciones exactas
    pos1 = None
    pos2 = None
    for i, sym in enumerate(card1.symbols):
        if sym == common_sym:
            pos1 = positions[i]
    for i, sym in enumerate(card2.symbols):
        if sym == common_sym:
            pos2 = positions2[i]
    
    if pos1 and pos2:
        # Línea curva conectando
        pygame.draw.line(surface, ACCENT_SUCCESS, pos1, pos2, 4)
        # Flecha en el medio
        mid_x = (pos1[0] + pos2[0]) // 2
        mid_y = (pos1[1] + pos2[1]) // 2
        font_arrow = pygame.font.Font(None, 48)
        arrow = font_arrow.render("⟷", True, ACCENT_SUCCESS)
        surface.blit(arrow, (mid_x - arrow.get_width() // 2, mid_y - arrow.get_height() // 2))
    
    # Etiquetas de las cartas
    font_label = pygame.font.Font(None, 40)
    label1 = font_label.render("Carta 1", True, WHITE)
    label2 = font_label.render("Carta 2", True, WHITE)
    surface.blit(label1, (x1 + cw // 2 - label1.get_width() // 2, y1 + ch + 10))
    surface.blit(label2, (x2 + cw // 2 - label2.get_width() // 2, y2 + ch + 10))
    
    # Info del símbolo común
    font_info = pygame.font.Font(None, 32)
    sprite_name = Card._symbol_map.get(str(common_sym), "desconocido")
    info_text = font_info.render(f"Símbolo común: {sprite_name} (ID: {common_sym})", True, ACCENT_SUCCESS)
    surface.blit(info_text, (total_w // 2 - info_text.get_width() // 2, total_h - 50))
    
    # Guardar
    output_dir = os.path.join(os.path.dirname(__file__), 'card_images')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'match_example.png')
    pygame.image.save(surface, output_path)
    print(f"\nGuardado: {output_path}")
    
    pygame.quit()

if __name__ == '__main__':
    main()