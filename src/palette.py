# Lospec 500 Palette - 42 colores
# Extraído de lospec500-1x.png

# === COLORES BASE (oscuros a claros) ===
DARKEST = (16, 18, 28)        # 0  #10121c - Negro azulado muy oscuro
DARK_PURPLE = (44, 30, 49)    # 1  #2c1e31 - Púrpura muy oscuro
MID_PURPLE = (107, 38, 67)    # 2  #6b2643 - Púrpura medio
BRIGHT_PURPLE = (172, 40, 71) # 3  #ac2847 - Púrpura brillante
RED = (236, 39, 63)           # 4  #ec273f - Rojo intenso
DARK_RED_BROWN = (148, 73, 58) # 5  #94493a - Marrón rojizo oscuro
ORANGE_RED = (222, 93, 58)    # 6  #de5d3a - Naranja rojizo
ORANGE = (233, 133, 55)       # 7  #e98537 - Naranja
GOLD = (243, 168, 51)         # 8  #f3a833 - Dorado

# Alias compatibilidad
BLACK = DARKEST
WHITE = (255, 255, 255)

# === MARRONES / TIERRAS ===
DARK_BROWN = (77, 53, 51)     # 9  #4d3533 - Marrón muy oscuro
MID_BROWN = (110, 76, 48)     # 10 #6e4c30 - Marrón medio
LIGHT_BROWN = (162, 109, 63)  # 11 #a26d3f - Marrón claro
BEIGE = (206, 146, 72)        # 12 #ce9248 - Beige
LIGHT_BEIGE = (218, 177, 99)  # 13 #dab163 - Beige claro
PALE_YELLOW = (232, 210, 130) # 14 #e8d282 - Amarillo pálido
CREAM = (247, 243, 183)       # 15 #f7f3b7 - Crema

# === VERDES / AZULES OSCUROS ===
DARK_TEAL = (30, 64, 68)      # 16 #1e4044 - Verde azulado muy oscuro
TEAL = (0, 101, 84)           # 17 #006554 - Verde azulado
GREEN = (38, 133, 76)         # 18 #26854c - Verde
LIGHT_GREEN = (90, 181, 82)   # 19 #5ab552 - Verde claro
BRIGHT_GREEN = (157, 230, 78) # 20 #9de64e - Verde brillante
CYAN = (0, 139, 139)          # 21 #008b8b - Cian
MINT = (98, 164, 119)         # 22 #62a477 - Menta
PALE_GREEN = (166, 203, 150)  # 23 #a6cb96 - Verde pálido
VERY_PALE_GREEN = (211, 238, 211) # 24 #d3eed3 - Verde muy pálido

# === AZULES / PURPURAS ===
DARK_BLUE_PURPLE = (62, 59, 101)  # 25 #3e3b65 - Azul púrpura oscuro
BLUE = (56, 89, 179)            # 26 #3859b3 - Azul
LIGHT_BLUE = (51, 136, 222)     # 27 #3388de - Azul claro
SKY_BLUE = (54, 197, 244)       # 28 #36c5f4 - Azul cielo
LIGHT_CYAN = (109, 234, 214)    # 29 #6dead6 - Cian claro
MID_PURPLE2 = (94, 91, 140)     # 30 #5e5b8c - Púrpura medio
LAVENDER = (140, 120, 165)      # 31 #8c78a5 - Lavanda
PALE_LAVENDER = (176, 167, 184) # 32 #b0a7b8 - Lavanda pálida
VERY_PALE_LAVENDER = (222, 206, 237) # 33 #deceed - Lavanda muy pálida

# === ROSAS / MAGENTAS ===
MAGENTA = (154, 77, 118)      # 34 #9a4d76 - Magenta
PINK = (200, 120, 175)        # 35 #c878af - Rosa
LIGHT_PINK = (204, 153, 255)  # 36 #cc99ff - Rosa claro (lila)
CORAL = (250, 110, 121)       # 37 #fa6e79 - Coral
SOFT_PINK = (255, 162, 172)   # 38 #ffa2ac - Rosa suave
PALE_PINK = (255, 209, 213)   # 39 #ffd1d5 - Rosa muy pálido
WARM_WHITE = (246, 232, 224)  # 40 #f6e8e0 - Blanco cálido
WHITE = (255, 255, 255)       # 41 #ffffff - Blanco puro

# === LISTAS ORGANIZADAS POR USO ===

# Para fondo de UI (oscuros -> claros)
UI_BACKGROUNDS = [DARKEST, DARK_PURPLE, MID_PURPLE, DARK_TEAL, DARK_BLUE_PURPLE]

# Para texto sobre fondos oscuros
UI_TEXT_LIGHT = [WHITE, CREAM, PALE_YELLOW, VERY_PALE_GREEN, WARM_WHITE]

# Para texto sobre fondos claros
UI_TEXT_DARK = [DARKEST, DARK_PURPLE, DARK_BROWN, MID_BROWN]

# Para acentos/botones (vibrantes)
UI_ACCENTS = [RED, ORANGE, GOLD, BRIGHT_GREEN, SKY_BLUE, CORAL, PINK]

# Para estados
SUCCESS = BRIGHT_GREEN
ERROR = RED
WARNING = GOLD
INFO = SKY_BLUE

# Para fallback de símbolos (16 colores vibrantes y distinguibles)
SYMBOL_FALLBACK = [
    RED,              # 4  - Rojo
    BLUE,             # 26 - Azul
    GREEN,            # 18 - Verde
    GOLD,             # 8  - Amarillo/Dorado
    MAGENTA,          # 34 - Magenta
    CYAN,             # 21 - Cian
    DARK_BROWN,       # 9  - Marrón
    TEAL,             # 17 - Verde azulado
    ORANGE,           # 7  - Naranja
    PINK,             # 35 - Rosa
    LAVENDER,         # 31 - Lavanda
    CORAL,            # 37 - Coral
    LIGHT_GREEN,      # 19 - Verde claro
    LIGHT_BLUE,       # 27 - Azul claro
    SOFT_PINK,        # 38 - Rosa suave
    MID_BROWN,        # 10 - Marrón medio
]

# Paleta completa como lista (índice = ID en imagen)
PALETTE = [
    DARKEST, DARK_PURPLE, MID_PURPLE, BRIGHT_PURPLE, RED,
    DARK_RED_BROWN, ORANGE_RED, ORANGE, GOLD,
    DARK_BROWN, MID_BROWN, LIGHT_BROWN, BEIGE, LIGHT_BEIGE, PALE_YELLOW, CREAM,
    DARK_TEAL, TEAL, GREEN, LIGHT_GREEN, BRIGHT_GREEN,
    CYAN, MINT, PALE_GREEN, VERY_PALE_GREEN,
    DARK_BLUE_PURPLE, BLUE, LIGHT_BLUE, SKY_BLUE, LIGHT_CYAN,
    MID_PURPLE2, LAVENDER, PALE_LAVENDER, VERY_PALE_LAVENDER,
    MAGENTA, PINK, LIGHT_PINK, CORAL, SOFT_PINK, PALE_PINK,
    WARM_WHITE, WHITE
]

def get_color(idx):
    """Obtiene color por índice (0-41) con wrap-around."""
    return PALETTE[idx % len(PALETTE)]

def hex_color(rgb):
    """Convierte tupla RGB a string hex."""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"