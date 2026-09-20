import math

import pygame

from constants import ACCENT_PRIMARY, BG_PANEL
from fonts import load_font

# Abreviaciones para mostrar teclas largas en la UI.
KEY_LABEL_SHORTHAND = {
    "space": "SPACE", "left shift": "LSHIFT", "right shift": "RSHIFT",
    "left ctrl": "LCTRL", "right ctrl": "RCTRL", "left alt": "LALT",
    "right alt": "RALT", "left meta": "LMETA", "right meta": "RMETA",
    "caps lock": "CAPS", "backspace": "BKSP", "delete": "DEL",
    "insert": "INS", "pageup": "PGUP", "pagedown": "PGDN",
    "home": "HOME", "end": "END", "return": "ENTER", "kpenter": "ENTER",
    "kp0": "0", "kp1": "1", "kp2": "2", "kp3": "3", "kp4": "4",
    "kp5": "5", "kp6": "6", "kp7": "7", "kp8": "8", "kp9": "9",
}


def breathe(amount=0.03, period=2.2):
    """Factor de escala (aprox 1-amount..1+amount) para animacion de respiracion."""
    t = pygame.time.get_ticks() / 1000.0
    return 1.0 + amount * math.sin(t * math.tau / period)


def fit_scaled(surface, scale):
    """Devuelve la superficie escalada por `scale` (o la misma si no cambia)."""
    w, h = surface.get_size()
    if w == 0 or h == 0:
        return surface
    sw = max(1, int(w * scale))
    sh = max(1, int(h * scale))
    if (sw, sh) == (w, h):
        return surface
    return pygame.transform.smoothscale(surface, (sw, sh))


def blit_breathing(surface, text_surf, rect, scale):
    """Dibuja el texto escalado (respirando) centrado en `rect`."""
    w, h = text_surf.get_size()
    if w == 0 or h == 0:
        surface.blit(text_surf, rect)
        return
    sw = max(1, int(w * scale))
    sh = max(1, int(h * scale))
    if (sw, sh) == (w, h):
        surface.blit(text_surf, rect)
        return
    scaled = pygame.transform.smoothscale(text_surf, (sw, sh))
    surface.blit(scaled, scaled.get_rect(center=rect.center))


def scaled_text(text, base_size, scale, color, alpha=255):
    """Renderiza texto y lo escala/altera alpha en una sola ayuda."""
    surf = load_font(base_size).render(text, True, color)
    if surf.get_width() == 0 or surf.get_height() == 0:
        return surf
    w = max(1, int(surf.get_width() * scale))
    h = max(1, int(surf.get_height() * scale))
    if (w, h) != (surf.get_width(), surf.get_height()):
        surf = pygame.transform.smoothscale(surf, (w, h))
    if alpha < 255:
        surf.set_alpha(alpha)
    return surf


def render_fitting_text(text, sizes, max_w, color):
    # --- AJUSTE DE FUENTE ---
    # `sizes` es una lista de tamaños de fuente, de mayor a menor,
    # que se prueban en orden: se usa el primer tamaño cuyo texto
    # quepa dentro de `max_w` píxeles de ancho (y no se dibuja nada
    # más grande). Cadena arriba = texto más gordo; cadena abajo =
    # texto más fino pero legible. Reduce la lista si quieres menos
    # escalones (p. ej. [38, 30, 22]) o agranda `max_w` para dar
    # más margen antes de recortar el texto.
    if not text:
        # Renderizar un espacio: una superficie de ancho 0 hace que
        # pygame.transform.smoothscale provoque un fallo (segfault).
        font = load_font(sizes[-1])
        return font, font.render(" ", True, color)
    ellipsis = "..."
    for size in sizes:
        font = load_font(size)
        if font.size(text)[0] <= max_w:
            return font, font.render(text, True, color)
    font = load_font(sizes[-1])
    ell_surf = font.render(ellipsis, True, color)
    e_w = ell_surf.get_width()
    if e_w >= max_w:
        return font, font.render(text[-1] if len(text) <= 2 else text[:2], True, color)
    remain = text
    while remain and font.size(remain)[0] + e_w > max_w:
        remain = remain[:-1]
    if not remain:
        return font, font.render(ellipsis, True, color)
    body = font.render(remain, True, color)
    out = pygame.Surface((body.get_width() + e_w, body.get_height()),
                         pygame.SRCALPHA)
    out.blit(body, (0, 0))
    out.blit(ell_surf, (body.get_width(), 0))
    return font, out


def blur_backdrop(surface):
    """Miniatura ampliada + velo oscuro: fondo difuminado para modales."""
    w, h = surface.get_size()
    small = pygame.transform.smoothscale(
        surface, (max(1, w // 8), max(1, h // 8)))
    blurred = pygame.transform.smoothscale(small, (w, h))
    veil = pygame.Surface((w, h), pygame.SRCALPHA)
    veil.fill((0, 0, 0, 130))
    blurred.blit(veil, (0, 0))
    return blurred


def draw_modal_panel(surface, win_w, win_h, w, h):
    """Panel centrado con borde acentuado; devuelve su rect."""
    rect = pygame.Rect((win_w - w) // 2, (win_h - h) // 2, w, h)
    panel_color = tuple(min(255, int(c * 1.08)) for c in BG_PANEL)
    pygame.draw.rect(surface, panel_color, rect, border_radius=16)
    pygame.draw.rect(surface, ACCENT_PRIMARY, rect, 3, border_radius=16)
    return rect


def blit_modal_shadow(surface, rect, radius=16):
    """Sombra sutil por capas bajo el panel, para dar profundidad."""
    pad = 14
    shadow = pygame.Surface((rect.w + 2 * pad, rect.h + 2 * pad),
                            pygame.SRCALPHA)
    body = pygame.Rect(pad, pad, rect.w, rect.h)
    body.move_ip(2, 10)
    pygame.draw.rect(shadow, (0, 0, 0, 70), body, border_radius=radius)
    body.move_ip(-2, -6)
    pygame.draw.rect(shadow, (0, 0, 0, 35), body, border_radius=radius)
    surface.blit(shadow, (rect.x - pad, rect.y - pad))


def draw_modal_ribbon(surface, rect, color, width=8):
    """Banda de acento translucida que corona el modal."""
    bar = pygame.Surface((rect.w, width + 4), pygame.SRCALPHA)
    bar.fill((*color[:3], 55))
    pygame.draw.rect(bar, (*color[:3], 235), (2, 0, rect.w - 4, width),
                     border_radius=width // 2)
    surface.blit(bar, (rect.x, rect.y + 8))


def key_display_name(key):
    if not key:
        return "-"
    value = key.upper()
    return KEY_LABEL_SHORTHAND.get(key.lower().replace(" ", ""), value)


def ease_out_cubic(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) ** 3


def ease_out_back(t):
    t = max(0.0, min(1.0, t))
    c1 = 1.70158
    c3 = c1 + 1.0
    t -= 1.0
    return 1.0 + c3 * t ** 3 + c1 * t ** 2