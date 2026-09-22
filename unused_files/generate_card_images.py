#!/usr/bin/env python3
"""Genera imágenes PNG de todas las cartas del juego DOBBLE para el tríptico."""
import pygame
import os
import sys

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from deck import Deck
from card import Card
from constants import ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT, ASSET_SYMBOL_SIZE

def main():
    # Inicializar pygame (sin ventana visible)
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    
    # Configurar tamaño de carta en alta resolución (assets nativos)
    Card.set_card_size(ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT)
    Card.set_layout(
        offset_x=40,
        offset_y=40,
        spacing=ASSET_CARD_WIDTH // 4,
        symbol_size=ASSET_SYMBOL_SIZE
    )
    
    # Generar mazo
    deck = Deck()
    print(f"Generando {len(deck.cards)} cartas...")
    
    # Crear directorio de salida
    output_dir = os.path.join(os.path.dirname(__file__), 'card_images')
    os.makedirs(output_dir, exist_ok=True)
    
    # Renderizar y guardar cada carta
    for card in deck.cards:
        surface = card.to_surface()
        filename = os.path.join(output_dir, f'card_{card.id:02d}.png')
        pygame.image.save(surface, filename)
        print(f"  Guardada: {filename}")
    
    # También generar una imagen de muestra con varias cartas
    generate_sample_grid(deck.cards, output_dir)
    
    pygame.quit()
    print(f"\n¡Listo! Imágenes guardadas en: {output_dir}")

def generate_sample_grid(cards, output_dir, cols=8, rows=4):
    """Genera una cuadrícula de muestra con 32 cartas."""
    card_w = ASSET_CARD_WIDTH
    card_h = ASSET_CARD_HEIGHT
    margin = 20
    
    grid_w = cols * card_w + (cols + 1) * margin
    grid_h = rows * card_h + (rows + 1) * margin
    
    grid_surface = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
    grid_surface.fill((30, 30, 40))  # Fondo oscuro
    
    for i, card in enumerate(cards[:cols * rows]):
        row = i // cols
        col = i % cols
        x = margin + col * (card_w + margin)
        y = margin + row * (card_h + margin)
        card_surf = card.to_surface()
        grid_surface.blit(card_surf, (x, y))
    
    grid_path = os.path.join(output_dir, 'sample_grid.png')
    pygame.image.save(grid_surface, grid_path)
    print(f"  Guardada cuadrícula de muestra: {grid_path}")

if __name__ == '__main__':
    main()