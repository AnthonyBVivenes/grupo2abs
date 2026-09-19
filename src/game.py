import os
import sys

import pygame

from constants import *
from deck import Deck
from player import Player


def load_font(size, bold=False):
    if os.path.exists(FONT_PATH_04B30):
        try:
            return pygame.font.Font(FONT_PATH_04B30, size)
        except (pygame.error, OSError):
            pass
    for name in [FONT_NAME] + FONT_FALLBACKS:
        path = pygame.font.match_font(name, bold=bold)
        if path:
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


class Game:
    def __init__(self):
        flags = pygame.RESIZABLE if WINDOW_RESIZABLE else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Dobble")
        self.clock = pygame.time.Clock()
        self.running = True
        self.w, self.h = SCREEN_WIDTH, SCREEN_HEIGHT

        self.state = "MENU"
        self.menu_index = 0
        self.menu_rects = []
        self.menu_msg = ""
        self.menu_msg_end = 0
        self.menu_options = [
            ("1 JUGADOR", self._new_game),
            ("MULTIJUGADOR LOCAL", self._menu_note),
            ("MULTIJUGADOR REMOTO", self._menu_note),
            ("CONFIGURACION", self._menu_note),
            ("SALIR", self._quit_game),
        ]

    def _new_game(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.center_card = self.deck.draw_card()
        self.players = [Player("Jugador 1", is_human=True)]
        for player in self.players:
            card = self.deck.draw_card()
            if card:
                player.add_card(card)
        self.game_over = False
        self.message = ""
        self.message_color = TEXT_PRIMARY
        self.message_end = 0
        self.feedback = []
        self.game_start = pygame.time.get_ticks()
        self.time_left = float(GAME_TIME_LIMIT)
        self.center_card_pos = (0, 0)
        self.player_card_pos = (0, 0)
        self.state = "PLAYING"

    def _menu_note(self):
        labels = [opt[0] for opt in self.menu_options]
        name = labels[self.menu_index]
        self.menu_msg = f"{name}: proximamente en desarrollo"
        self.menu_msg_end = pygame.time.get_ticks() + 2000

    def _quit_game(self):
        self.running = False

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.w, self.h = event.w, event.h
                self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

    def handle_key(self, key):
        if self.state == "MENU":
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(self.menu_options)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(self.menu_options)
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                _, callback = self.menu_options[self.menu_index]
                callback()
            elif key == pygame.K_ESCAPE:
                self.running = False
        elif key == pygame.K_ESCAPE:
            self.state = "MENU"
        elif key == pygame.K_r and self.game_over:
            self._new_game()

    def update(self):
        if self.state == "PLAYING" and not self.game_over:
            elapsed = (pygame.time.get_ticks() - self.game_start) / 1000
            self.time_left = max(0.0, GAME_TIME_LIMIT - elapsed)
            if self.time_left <= 0:
                self._end_game()

    def handle_click(self, pos):
        if self.state == "MENU":
            for index, rect in enumerate(self.menu_rects):
                if rect.collidepoint(pos):
                    self.menu_index = index
                    _, callback = self.menu_options[index]
                    callback()
                    return
            return
        if self.game_over:
            return
        player = self.players[0]
        if not player.hand:
            return
        card = player.hand[0]
        px, py = self.player_card_pos
        if px <= pos[0] <= px + CARD_WIDTH and py <= pos[1] <= py + CARD_HEIGHT:
            hit = card.get_symbol_at_pos(pos[0] - px, pos[1] - py)
            if hit:
                sym, index = hit
                rel_x, rel_y, _ = card._symbol_positions[index]
                click_pos = (px + rel_x, py + rel_y)
                if sym in self.center_card.symbols:
                    self._on_correct(player, card, index, click_pos)
                else:
                    self._on_incorrect(player, index, click_pos)

    def _add_feedback(self, kind, pos):
        self.feedback.append({
            "kind": kind,
            "pos": pos,
            "start": pygame.time.get_ticks(),
            "duration": 900,
        })

    def _on_correct(self, player, card, index=0, pos=(0, 0)):
        player.score += 1
        player.correct += 1
        self._add_feedback("correct", pos)
        player.remove_card(card)
        next_center = self.deck.draw_card()
        if next_center is None:
            self._end_game()
            return
        self.center_card = next_center
        if self.deck.remaining() == 0:
            self._end_game()
            return
        replacement = self.deck.draw_card()
        if replacement:
            player.add_card(replacement)
        self.show_message("Coincidencia!", ACCENT_SUCCESS)

    def _on_incorrect(self, player, index=0, pos=(0, 0)):
        player.incorrect += 1
        self._add_feedback("incorrect", pos)
        card = player.hand[0]
        if card:
            for sym, rel in zip(card.symbols, card._symbol_positions):
                if sym in self.center_card.symbols:
                    px, py = self.player_card_pos
                    hint_pos = (px + rel[0], py + rel[1])
                    self._add_feedback("hint", hint_pos)
                    break
        self.show_message("No coincide!", ACCENT_ERROR)

    def _end_game(self):
        self.game_over = True
        self.message = "FIN DE PARTIDA"
        self.message_color = ACCENT_WARNING
        self.message_end = pygame.time.get_ticks() + 60000

    def show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_end = pygame.time.get_ticks() + 1600

    def render(self):
        screen = self.screen
        if self.state == "MENU":
            self._render_menu(screen)
        else:
            self._render_game(screen)
        pygame.display.flip()

    def _render_menu(self, screen):
        screen.fill(BG_COLOR)
        title_font = load_font(FONT_SIZE_TITLE)
        subtitle_font = load_font(18)
        label_font = load_font(FONT_SIZE_MENU)
        hint_font = load_font(16)
        msg_font = load_font(FONT_SIZE_SMALL)

        center_x = self.w // 2

        title = title_font.render("DOBBLE", True, ACCENT_PRIMARY)
        screen.blit(title, title.get_rect(center=(center_x, 120)))

        subtitle = subtitle_font.render("Encuentra el simbolo comun", True, TEXT_SECONDARY)
        screen.blit(subtitle, subtitle.get_rect(center=(center_x, 170)))

        option_h = label_font.get_height() + 24
        start_y = self.h // 2 - (option_h * len(self.menu_options)) // 2 + 30

        self.menu_rects = []
        for index, (label, _) in enumerate(self.menu_options):
            selected = index == self.menu_index
            color = ACCENT_PRIMARY if selected else TEXT_SECONDARY
            rendered = label_font.render(label, True, color)
            rect = rendered.get_rect(center=(center_x, start_y + index * option_h))
            if selected:
                padding = rendered.get_rect().inflate(40, 16)
                padding.center = rect.center
                pygame.draw.rect(screen, BG_PANEL, padding, border_radius=8)
                pygame.draw.rect(screen, ACCENT_PRIMARY, padding, 2, border_radius=8)
                screen.blit(rendered, rect)
            else:
                screen.blit(rendered, rect)
            self.menu_rects.append(rect)

        hints = "Arriba/Abajo o W/S: mover   Enter/Espacio: elegir   Esc: salir"
        hint = hint_font.render(hints, True, TEXT_MUTED)
        screen.blit(hint, hint.get_rect(center=(center_x, self.h - 50)))

        if self.menu_msg and pygame.time.get_ticks() < self.menu_msg_end:
            msg = msg_font.render(self.menu_msg, True, ACCENT_WARNING)
            screen.blit(msg, msg.get_rect(center=(center_x, self.h - 90)))

    def _render_game(self, screen):
        screen.fill(BG_COLOR)
        self._draw_stats_panel(screen)
        self._draw_timer(screen)
        if self.center_card:
            play_left = SCORE_PANEL_WIDTH
            play_w = self.w - play_left
            cx = play_left + play_w // 2 - CARD_WIDTH // 2
            cy = 70
            self.center_card_pos = (cx, cy)
            self.center_card.draw(screen, cx, cy)
            if self.players and self.players[0].hand:
                py = cy + CARD_HEIGHT + 70
                self.player_card_pos = (cx, py)
                self.players[0].hand[0].draw(screen, cx, py)
        self._draw_feedback(screen)
        self._draw_message(screen)
        if self.game_over:
            self._draw_game_over(screen)
        pygame.display.flip()

    def _draw_timer(self, screen):
        if self.time_left <= 0:
            return
        seconds = int(self.time_left)
        text = f"{seconds // 60:02d}:{seconds % 60:02d}"
        font = load_font(30)

        if self.time_left <= 5 and (pygame.time.get_ticks() // 500) % 2 == 0:
            color = ACCENT_ERROR
        elif self.time_left <= 10:
            color = ACCENT_ERROR
        elif self.time_left <= 15:
            color = ACCENT_WARNING
        else:
            color = TEXT_PRIMARY

        center_x = SCORE_PANEL_WIDTH + (self.w - SCORE_PANEL_WIDTH) // 2
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(center_x, 34))

        banner = rendered.get_rect().inflate(24, 12)
        banner.center = rect.center
        pygame.draw.rect(screen, BG_PANEL, banner, border_radius=8)
        pygame.draw.rect(screen, color, banner, 2, border_radius=8)
        screen.blit(rendered, rect)

        bar_w = 180
        bar_x = center_x - bar_w // 2
        bar_y = rect.bottom + 8
        bar = pygame.Rect(bar_x, bar_y, bar_w, 8)
        pygame.draw.rect(screen, BG_PANEL, bar, border_radius=4)
        ratio = max(0.0, min(1.0, self.time_left / GAME_TIME_LIMIT))
        fill = pygame.Rect(bar_x, bar_y, int(bar_w * ratio), 8)
        pygame.draw.rect(screen, color, fill, border_radius=4)
        pygame.draw.rect(screen, BORDER, bar, 1, border_radius=4)

    def _draw_stats_panel(self, screen):
        panel = pygame.Rect(0, 0, SCORE_PANEL_WIDTH, self.h)
        pygame.draw.rect(screen, BG_SECONDARY, panel)
        pygame.draw.line(screen, BORDER, (SCORE_PANEL_WIDTH - 1, 0),
                         (SCORE_PANEL_WIDTH - 1, self.h), 2)

        title_font = load_font(18)
        label_font = load_font(FONT_SIZE_SMALL)
        value_font = load_font(FONT_SIZE_SCORE)

        center_x = SCORE_PANEL_WIDTH // 2

        def center_text(surface, text, y, font, color):
            rendered = font.render(text, True, color)
            rect = rendered.get_rect(center=(center_x, y))
            surface.blit(rendered, rect)

        center_text(screen, "DOBBLE", 30, title_font, ACCENT_PRIMARY)

        player = self.players[0]
        center_text(screen, player.name, 66, label_font, PLAYER1_COLOR)
        center_text(screen, str(player.score), 96, value_font, TEXT_PRIMARY)

        panel_line = 130
        pygame.draw.line(screen, BORDER, (20, panel_line), (SCORE_PANEL_WIDTH - 20, panel_line), 1)

        center_text(screen, "Correctas", 156, label_font, TEXT_SECONDARY)
        center_text(screen, str(player.correct), 180, value_font, ACCENT_SUCCESS)
        center_text(screen, "Fallos", 216, label_font, TEXT_SECONDARY)
        center_text(screen, str(player.incorrect), 240, value_font, ACCENT_ERROR)

        pygame.draw.line(screen, BORDER, (20, panel_line + 130), (SCORE_PANEL_WIDTH - 20, panel_line + 130), 1)

        center_text(screen, "Mazo", 296, label_font, TEXT_SECONDARY)
        center_text(screen, str(self.deck.remaining()), 320, value_font, TEXT_PRIMARY)

    def _draw_feedback(self, screen):
        if not self.feedback:
            return
        now = pygame.time.get_ticks()
        active = []
        for fb in self.feedback:
            t = (now - fb["start"]) / fb["duration"]
            if t < 1.0:
                active.append((fb, t))
        self.feedback = [fb for fb, _ in active]
        if not active:
            return

        glow = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for fb, t in active:
            kind = fb["kind"]
            color = ACCENT_SUCCESS if kind in ("correct", "hint") else ACCENT_ERROR
            x, y = fb["pos"]
            radius = SYMBOL_SIZE // 2 + int((SYMBOL_SIZE + 24) * t)
            alpha = int(255 * (1 - t))
            width = max(3, int(7 * (1 - t)) + 2)

            inner = int(SYMBOL_SIZE // 2 * (0.5 + 0.5 * t))
            pygame.draw.circle(glow, (color[0], color[1], color[2], 70), (x, y), inner)

            if kind in ("correct", "incorrect"):
                pygame.draw.circle(glow, (color[0], color[1], color[2], alpha), (x, y), radius, width)
                ring2_r = int(radius * 0.6)
                pygame.draw.circle(glow, (color[0], color[1], color[2], int(alpha * 0.5)), (x, y), ring2_r, max(1, width // 2))
            else:
                half = int(SYMBOL_SIZE * (0.4 + 0.5 * t))
                pygame.draw.circle(glow, (color[0], color[1], color[2], alpha), (x, y), half, 4)
        screen.blit(glow, (0, 0))

    def _draw_message(self, screen):
        if not self.message or self.game_over:
            return
        now = pygame.time.get_ticks()
        if now >= self.message_end:
            return
        font = load_font(FONT_SIZE_MESSAGE)

        gap_top = self.center_card_pos[1] + CARD_HEIGHT
        gap_bottom = self.player_card_pos[1]
        if gap_bottom <= gap_top:
            gap_top = 80
            gap_bottom = self.h - 80
        my = (gap_top + gap_bottom) // 2

        max_width = self.w - SCORE_PANEL_WIDTH - 60
        lines = []
        current = ""
        for word in self.message.split():
            test = current + " " + word if current else word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        line_h = font.get_height() + 6
        height = line_h * len(lines)
        width = max(font.size(line)[0] for line in lines) + 40
        center_x = SCORE_PANEL_WIDTH + (self.w - SCORE_PANEL_WIDTH) // 2

        fade = 1.0
        remaining = self.message_end - now
        if remaining < 350:
            fade = remaining / 350

        banner = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_alpha = int(200 * fade)
        pygame.draw.rect(banner, (*BG_COLOR, bg_alpha), banner.get_rect(), border_radius=12)
        pygame.draw.rect(banner, (*self.message_color, int(220 * fade)),
                         banner.get_rect(), 3, border_radius=12)

        start_y = height // 2 - (line_h * (len(lines) - 1)) // 2
        for i, line in enumerate(lines):
            rendered = font.render(line, True, self.message_color)
            rect = rendered.get_rect(center=(banner.get_width() // 2, start_y + i * line_h))
            banner.blit(rendered, rect)

        screen.blit(banner, banner.get_rect(center=(center_x, my)))

    def _draw_game_over(self, screen):
        player = self.players[0]
        total = player.correct + player.incorrect
        precision = (player.correct / total * 100) if total else 0.0
        lines = [
            "FIN DE PARTIDA",
            f"Puntos: {player.score}",
            f"Correctas: {player.correct}",
            f"Fallos: {player.incorrect}",
            f"Precision: {precision:.1f}%",
            "R: reiniciar   Esc: menu",
        ]
        font = load_font(26)
        line_h = font.get_height() + 8
        center_x = SCORE_PANEL_WIDTH + (self.w - SCORE_PANEL_WIDTH) // 2
        start_y = self.h // 2 - (line_h * len(lines)) // 2
        for i, line in enumerate(lines):
            color = TEXT_PRIMARY
            if i == 0:
                color = ACCENT_PRIMARY
            rendered = font.render(line, True, color)
            rect = rendered.get_rect(center=(center_x, start_y + i * line_h))
            screen.blit(rendered, rect)