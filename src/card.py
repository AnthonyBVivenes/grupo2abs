import pygame
import os
import json
from constants import (
    CARD_WIDTH, CARD_HEIGHT, SYMBOL_SIZE, WHITE, BLACK,
    SPRITES_DIR, SYMBOLS_PER_CARD,
    SYMBOL_FALLBACK, HIGHLIGHT, BORDER, BORDER_LIGHT,
    SCALE_FACTOR, ASSET_CARD_WIDTH, ASSET_CARD_HEIGHT, ASSET_SYMBOL_SIZE,
    RED, ACCENT_SUCCESS, ACCENT_ERROR, ACCENT_INFO, ACCENT_WARNING,
    HIGHLIGHT, PALE_YELLOW
)
from fonts import load_font

class Card:
    # --- Cachés y estado compartido (clase, no instancia) ---
    _sprite_cache = {}      # {symbol_id: pygame.Surface} - sprites ya escalados
    _card_base = None       # pygame.Surface - imagen base de la carta escalada
    _symbol_map = None      # dict - mapeo symbol_id -> nombre_archivo.png
    _layout_params = {      # Parámetros de layout mutables para editor visual (en píxeles de RENDER)
        'offset_x': 20,     # Margen izquierdo desde borde carta
        'offset_y': 20,     # Margen superior desde borde carta
        'spacing': None,    # Espacio entre centros de slots (None = auto)
        'symbol_size': 50,  # Tamaño del símbolo en píxeles de RENDER
    }

    @classmethod
    def get_layout(cls):
        """Devuelve copia de los parámetros de layout actuales."""
        return cls._layout_params.copy()

    @classmethod
    def set_layout(cls, **kwargs):
        """Actualiza parámetros de layout (usado por editor visual)."""
        cls._layout_params.update(kwargs)

    @classmethod
    def reset_layout(cls):
        """Restaura valores por defecto del layout."""
        cls._layout_params = {
            'offset_x': 20,
            'offset_y': 20,
            'spacing': None,
            'symbol_size': 30,
        }

    def __init__(self, card_id, symbols):
        """Inicializa una carta con su ID único y lista de 8 símbolos (ints 0-56)."""
        self.id = card_id           # Identificador único de la carta (0-56)
        self.symbols = symbols      # Lista de 8 IDs de símbolos en esta carta
        self.image = None           # No usado actualmente (reservado)
        self.rect = None            # pygame.Rect - área de colisión (click)
        self._symbol_positions = []  # Se llena en draw() o calculate_positions()
        self._key_labels = []        # Etiquetas de teclas para cada símbolo
        self._calculate_positions(0, 0)  # Inicializar posiciones relativas (0,0)

    def _calculate_positions(self, x, y):
        """Calcula las posiciones de los símbolos relativas a la esquina de la carta."""
        layout = self._layout_params
        spacing = layout['spacing'] if layout['spacing'] is not None else \
                  CARD_WIDTH // 4
        offset_x = layout['offset_x']
        offset_y = layout['offset_y']
        symbol_size = layout['symbol_size']
        
        row_spacing = symbol_size + 10
        
        card_center_x = x + CARD_WIDTH // 2
        card_center_y = y + CARD_HEIGHT // 2
        
        positions = [
            (card_center_x - spacing, card_center_y - row_spacing),
            (card_center_x, card_center_y - row_spacing),
            (card_center_x + spacing, card_center_y - row_spacing),
            (card_center_x - spacing // 2, card_center_y),
            (card_center_x + spacing // 2, card_center_y),
            (card_center_x - spacing, card_center_y + row_spacing),
            (card_center_x, card_center_y + row_spacing),
            (card_center_x + spacing, card_center_y + row_spacing),
        ]
        
        # Guardar posiciones RELATIVAS a la esquina de la carta (x,y)
        self._symbol_positions = [(cx - x, cy - y, sym) for (cx, cy), sym in zip(positions, self.symbols)]

    def set_key_labels(self, labels):
        """Asigna etiquetas de teclas a los símbolos (lista de 8 strings)."""
        self._key_labels = labels[:8] if labels else []

    @classmethod
    def _load_symbol_map(cls):
        """Carga symbol_map.json una sola vez (lazy loading)."""
        if cls._symbol_map is None:
            map_path = os.path.join(SPRITES_DIR, 'symbol_map.json')
            if os.path.exists(map_path):
                with open(map_path, 'r') as f:
                    cls._symbol_map = json.load(f)
            else:
                cls._symbol_map = {}

    @classmethod
    def get_card_base(cls):
        """Carga la imagen base de la carta en resolución nativa (lazy loading)."""
        if cls._card_base is None:
            base_path = os.path.join(SPRITES_DIR, 'baseDEcartaEscalada.png')
            if os.path.exists(base_path):
                cls._card_base = pygame.image.load(base_path).convert_alpha()
            else:
                cls._card_base = None
        return cls._card_base

    @classmethod
    def get_sprite(cls, symbol_id):
        """Obtiene sprite en resolución nativa (con caché)."""
        cls._load_symbol_map()
        if symbol_id not in cls._sprite_cache:
            filename = cls._symbol_map.get(str(symbol_id))
            if filename:
                sprite_path = os.path.join(SPRITES_DIR, filename)
                if os.path.exists(sprite_path):
                    cls._sprite_cache[symbol_id] = pygame.image.load(sprite_path).convert_alpha()
                else:
                    cls._sprite_cache[symbol_id] = None
            else:
                cls._sprite_cache[symbol_id] = None
        return cls._sprite_cache[symbol_id]

    def draw(self, surface, x, y, debug=False):
        """Dibuja la carta completa en la surface dada en posición (x, y)."""
        # 1. Rectángulo base de la carta (para colisiones y fondo)
        rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

        # 2. Fondo: imagen base si existe, sino rectángulo blanco
        # Escalar la base de carta en tiempo de render (assets HD -> render size)
        card_base = self.get_card_base()
        if card_base:
            scaled_base = pygame.transform.scale(card_base, (CARD_WIDTH, CARD_HEIGHT))
            surface.blit(scaled_base, (x, y))
        else:
            pygame.draw.rect(surface, WHITE, rect)

        # 3. Borde negro siempre visible (2px)
        pygame.draw.rect(surface, BLACK, rect, 2)

        # 5. Paleta de 16 colores fallback para símbolos sin sprite (Lospec 500)
        fallback_colors = SYMBOL_FALLBACK

        # 6. Calcular layout 3-2-3 centrado verticalmente en la carta
        layout = self._layout_params
        spacing = layout['spacing'] if layout['spacing'] is not None else \
                  CARD_WIDTH // 4
        offset_x = layout['offset_x']
        symbol_size = layout['symbol_size']
        
        # Espaciado vertical entre filas
        row_spacing = symbol_size + 10
        
        # Centrar el bloque de 3 filas verticalmente en la carta
        card_center_x = x + CARD_WIDTH // 2
        card_center_y = y + CARD_HEIGHT // 2
        
        positions = [
            (card_center_x - spacing, card_center_y - row_spacing),
            (card_center_x, card_center_y - row_spacing),
            (card_center_x + spacing, card_center_y - row_spacing),
            (card_center_x - spacing // 2, card_center_y),
            (card_center_x + spacing // 2, card_center_y),
            (card_center_x - spacing, card_center_y + row_spacing),
            (card_center_x, card_center_y + row_spacing),
            (card_center_x + spacing, card_center_y + row_spacing),
        ]

        # 7. Bucle principal: dibujar cada uno de los 8 símbolos en sus posiciones
        for i, sym in enumerate(self.symbols):
            cx, cy = positions[i]

            # 8. Intentar cargar sprite real; si no existe, círculo de color
            sprite = self.get_sprite(sym)
            if sprite:
                # Escalar sprite en tiempo de render al symbol_size objetivo
                scaled_sprite = pygame.transform.scale(sprite, (symbol_size, symbol_size))
                sprite_rect = scaled_sprite.get_rect(center=(cx, cy))
                surface.blit(scaled_sprite, sprite_rect)
            else:
                color = fallback_colors[sym % len(fallback_colors)]
                pygame.draw.circle(surface, color, (cx, cy), symbol_size // 2)

            # Dibujar etiqueta de tecla si existe
            if i < len(self._key_labels) and self._key_labels[i]:
                self._draw_key_label(surface, cx, cy, self._key_labels[i], symbol_size)

        # 9. Overlay debug si está activado (tecla D)
        if debug:
            self._draw_debug(surface, x, y, offset_x, 0, spacing, symbol_size)

        # 10. Guardar rect para detección de clicks
        self.rect = rect
        # Guardar posiciones de símbolos RELATIVAS a la esquina superior-izquierda de la carta
        self._symbol_positions = [(cx - x, cy - y, sym) for (cx, cy), sym in zip(positions, self.symbols)]

    def get_symbol_at_pos(self, mouse_x, mouse_y):
        """Devuelve (symbol_id, index) si el click está sobre un símbolo, sino None."""
        for cx, cy, sym in self._symbol_positions:
            half = self._layout_params['symbol_size'] // 2
            if cx - half <= mouse_x <= cx + half and cy - half <= mouse_y <= cy + half:
                return (sym, self.symbols.index(sym))
        return None

    def get_symbol_by_key(self, key):
        """Devuelve (symbol_id, index) si la tecla coincide con una etiqueta, sino None."""
        for i, label in enumerate(self._key_labels):
            if label and label.upper() == key.upper():
                return (self.symbols[i], i)
        return None

    def _draw_key_label(self, surface, cx, cy, label, symbol_size):
        """Dibuja la etiqueta de tecla encima del símbolo."""
        font = load_font(max(14, symbol_size // 3))
        text = font.render(label.upper(), True, (255, 255, 255))
        # Fondo semitransparente para legibilidad
        bg_rect = text.get_rect(center=(cx, cy - symbol_size // 2 - 8))
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect.inflate(8, 4), border_radius=4)
        surface.blit(text, bg_rect)

    def _draw_debug(self, surface, x, y, offset_x, offset_y_unused, spacing, symbol_size):
        """Dibuja overlay de depuración: grid, IDs, coords, cruz central, info."""
        line_color = RED  # Rojo para líneas de grid

        # --- Layout 3-2-3 centrado: recalcular posiciones igual que en draw() ---
        card_center_x = x + CARD_WIDTH // 2
        card_center_y = y + CARD_HEIGHT // 2
        row_spacing = symbol_size + 10
        
        positions = [
            (card_center_x - spacing, card_center_y - row_spacing),
            (card_center_x, card_center_y - row_spacing),
            (card_center_x + spacing, card_center_y - row_spacing),
            (card_center_x - spacing // 2, card_center_y),
            (card_center_x + spacing // 2, card_center_y),
            (card_center_x - spacing, card_center_y + row_spacing),
            (card_center_x, card_center_y + row_spacing),
            (card_center_x + spacing, card_center_y + row_spacing),
        ]

        # --- Grid de referencia para layout 3-2-3 centrado ---
        # Líneas horizontales (centro de cada fila ± symbol_size/2)
        for row_offset in [-row_spacing, 0, row_spacing]:
            gy = card_center_y + row_offset - symbol_size // 2
            pygame.draw.line(surface, line_color, (x, gy), (x + CARD_WIDTH, gy), 1)
        
        # Líneas verticales guía (centro y ±spacing)
        for col_offset in [-spacing, 0, spacing]:
            gx = card_center_x + col_offset - symbol_size // 2
            pygame.draw.line(surface, line_color, (gx, y), (gx, y + CARD_HEIGHT), 1)

        # --- Cruz central verde éxito (centro geométrico de la carta) ---
        cx_center = x + CARD_WIDTH // 2
        cy_center = y + CARD_HEIGHT // 2
        pygame.draw.line(surface, ACCENT_SUCCESS, (cx_center - 10, cy_center), (cx_center + 10, cy_center), 2)
        pygame.draw.line(surface, ACCENT_SUCCESS, (cx_center, cy_center - 10), (cx_center, cy_center + 10), 2)

        # --- Info de cada slot: ID + índice ---
        font = pygame.font.Font(None, 16)
        row_labels = ["Fila 0", "Fila 0", "Fila 0", "Fila 1", "Fila 1", "Fila 2", "Fila 2", "Fila 2"]
        for i, sym in enumerate(self.symbols):
            cx, cy = positions[i]

            # Marco dorado del área del símbolo
            slot_rect = pygame.Rect(cx - symbol_size//2, cy - symbol_size//2, symbol_size, symbol_size)
            pygame.draw.rect(surface, HIGHLIGHT, slot_rect, 1)

            # Etiqueta "ID:N" con fondo negro legible
            id_text = font.render(f"ID:{sym}", True, WHITE)
            bg_rect = id_text.get_rect(topleft=(cx - 15, cy - symbol_size//2 - 18))
            pygame.draw.rect(surface, BLACK, bg_rect.inflate(4, 2))
            surface.blit(id_text, bg_rect)

            # Etiqueta de fila
            row_text = font.render(row_labels[i], True, PALE_YELLOW)
            surface.blit(row_text, (cx - 20, cy + symbol_size//2 + 2))

        # --- Borde exterior info + info de parámetros de layout ---
        pygame.draw.rect(surface, ACCENT_INFO, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        margin_font = pygame.font.Font(None, 14)
        margin_text = margin_font.render(
            f"offset_x:{offset_x} spacing:{spacing} symbol_size:{symbol_size} layout:3-2-3",
            True, HIGHLIGHT
        )
        surface.blit(margin_text, (x, y - 20))
