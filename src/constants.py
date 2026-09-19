# Constantes del juego + Paleta Lospec 500
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (
    PALETTE, SYMBOL_FALLBACK,
    DARKEST, DARK_PURPLE, MID_PURPLE, RED, GOLD,
    GREEN, BLUE, CYAN, WHITE, BLACK,
    TEAL, ORANGE, MAGENTA, PINK, CORAL,
    SKY_BLUE, LAVENDER, CREAM, WARM_WHITE,
    SUCCESS, ERROR, WARNING, INFO,
    UI_BACKGROUNDS, UI_TEXT_LIGHT, UI_TEXT_DARK, UI_ACCENTS,
    hex_color, get_color, PALE_YELLOW
)

# Ventana redimensionable y más compacta por defecto
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
WINDOW_RESIZABLE = True  # Ventana ajustable

# Tamaños de assets en alta resolución (opción E)
ASSET_CARD_WIDTH = 640
ASSET_CARD_HEIGHT = 750
ASSET_SYMBOL_SIZE = 160

# Tamaños de render en pantalla (escalados)
CARD_WIDTH = 200
CARD_HEIGHT = int(CARD_WIDTH * ASSET_CARD_HEIGHT / ASSET_CARD_WIDTH)  # 234 aprox
SYMBOL_SIZE = int(ASSET_SYMBOL_SIZE * CARD_WIDTH / ASSET_CARD_WIDTH)  # 50 aprox

# Factor de escala asset -> render
SCALE_FACTOR = CARD_WIDTH / ASSET_CARD_WIDTH  # ~0.3125

# Fuentes
FONT_NAME = "dejavusansmono"  # pygame font name (Consolas-like)
FONT_BOLD = "dejavusansmono"
FONT_FALLBACKS = ["ubuntumono", "liberationmono", "notomono", "freemono"]
FONT_PATH_04B30 = os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', '04b_30.ttf')

# Tamaños de fuente base
# ---------------------------------------------------------------------------
# TAMANOS DE FUENTE — ajusta aqui el tamano base de cada zona del juego.
# Estos valores se cargan via load_font(FONT_SIZE_*) en game.py; si un texto
# no cabe en su caja, game.py lo reduce automaticamente con _render_fitting_text.
# ---------------------------------------------------------------------------
FONT_SIZE_TITLE = 64
FONT_SIZE_MENU = 38
FONT_SIZE_GAME = 26    # Texto principal del juego / cartas
FONT_SIZE_SMALL = 20
FONT_SIZE_DEBUG = 14
FONT_SIZE_MESSAGE = 36  # Mensajes de feedback (más pequeño)
FONT_SIZE_SCORE = 28   # Puntuación jugadores

# Colores principales (compatibilidad + paleta)
WHITE = WHITE
BLACK = BLACK
RED = RED
BLUE = BLUE
GREEN = GREEN
GRAY = DARK_PURPLE

# Colores UI con paleta Lospec500
BG_COLOR = DARKEST           # Fondo pantalla
BG_SECONDARY = DARK_PURPLE   # Paneles secundarios
BG_PANEL = MID_PURPLE        # Paneles editor/debug
TEXT_PRIMARY = WHITE         # Texto principal
TEXT_SECONDARY = CREAM       # Texto secundario
TEXT_MUTED = PALE_YELLOW     # Texto apagado
ACCENT_PRIMARY = GOLD        # Acento principal
ACCENT_SECONDARY = ORANGE    # Acento secundario
ACCENT_SUCCESS = SUCCESS     # Verde éxito
ACCENT_ERROR = ERROR         # Rojo error
ACCENT_WARNING = WARNING     # Amarillo warning
ACCENT_INFO = INFO           # Azul info
HIGHLIGHT = GOLD             # Highlight cartas
BORDER = TEAL                # Bordes
BORDER_LIGHT = SKY_BLUE      # Bordes claros

# Colores específicos para jugadores (basados en paleta Lospec500)
PLAYER1_COLOR = SKY_BLUE     # Jugador 1 - azul cielo
PLAYER2_COLOR = CORAL        # Jugador 2 - coral/rojo suave
PLAYER1_BG = (30, 64, 68)    # Fondo jugador 1 - DARK_TEAL
PLAYER2_BG = (107, 38, 67)   # Fondo jugador 2 - MID_PURPLE

# Posiciones UI
MESSAGE_Y = SCREEN_HEIGHT // 2 - 100  # Mensaje feedback más arriba
SCORE_PANEL_WIDTH = 220

# Temporizador de partida (1 jugador) en segundos
GAME_TIME_LIMIT = 60

TOTAL_SYMBOLS = 57
SYMBOLS_PER_CARD = 8

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, '..', 'assets')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')
SOUNDS_DIR = os.path.join(ASSETS_DIR, 'sounds')
FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')
LAYOUT_FILE = os.path.join(ASSETS_DIR, 'card_layout.json')