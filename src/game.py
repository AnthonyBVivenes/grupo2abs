import os
import sys

import pygame

from card import Card
from constants import *
from config import Config
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


P1_KEYS = ["Q", "W", "E", "R", "A", "S", "D", "F"]
P2_KEYS = ["1", "2", "3", "4", "5", "6", "7", "8"]
INPUT_LOCK_MS = 300
SYMBOL_SIZES = {"small": 40, "normal": 50, "large": 60}


class Game:
    def __init__(self):
        self.config = Config()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), self._window_flags())
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
            ("MULTIJUGADOR LOCAL", self._new_local_game),
            ("MULTIJUGADOR REMOTO", self._menu_note),
            ("CONFIGURACION", self._open_settings),
            ("SALIR", self._quit_game),
        ]

        self.settings_index = 0
        self.settings_rects = []
        self.editing = None
        self.settings_rows = [
            {"label": "Duracion de partida", "type": "choice", "key": "time_limit",
             "values": [0, 30, 60, 90], "labels": ["Sin limite", "30s", "60s", "90s"]},
            {"label": "Tamano de cartas", "type": "choice", "key": "card_scale",
             "values": ["small", "normal", "large"], "labels": ["Pequena", "Normal", "Grande"],
             "apply": self._apply_card_scale},
            {"label": "Pista al fallar", "type": "choice", "key": "hint_on_error",
             "values": [False, True], "labels": ["No", "Si"]},
            {"label": "Penalizacion por fallo", "type": "choice", "key": "miss_penalty",
             "values": ["none", "light", "strong"], "labels": ["Ninguna", "Leve", "Fuerte"]},
            {"label": "Nombre Jugador 1", "type": "text", "key": "player_names", "index": 0},
            {"label": "Nombre Jugador 2", "type": "text", "key": "player_names", "index": 1},
            {"label": "Pantalla completa", "type": "choice", "key": "fullscreen",
             "values": [False, True], "labels": ["Ventana", "Pantalla completa"],
             "apply": self._apply_fullscreen},
            {"label": "Pausa tras acierto", "type": "choice", "key": "input_lock_ms",
             "values": [150, 300, 500], "labels": ["0.15s", "0.30s", "0.50s"]},
        ]

    def _window_flags(self):
        flags = pygame.RESIZABLE if WINDOW_RESIZABLE else 0
        if self.config["fullscreen"]:
            flags |= pygame.FULLSCREEN
        return flags

    def _apply_fullscreen(self):
        try:
            self.screen = pygame.display.set_mode(self.screen.get_size(), self._window_flags())
        except pygame.error:
            self.config["fullscreen"] = False
            self.screen = pygame.display.set_mode((self.w, self.h),
                                                  pygame.RESIZABLE if WINDOW_RESIZABLE else 0)

    def _apply_card_scale(self):
        Card.set_layout(symbol_size=SYMBOL_SIZES.get(self.config["card_scale"], 50))

    def _open_settings(self):
        self.state = "SETTINGS"
        self.settings_index = 0
        self.editing = None

    def _reset_state(self):
        self.game_over = False
        self.message = ""
        self.message_color = TEXT_PRIMARY
        self.message_end = 0
        self.feedback = []
        self.game_start = pygame.time.get_ticks()
        self.time_left = float(self.config["time_limit"] if self.config["time_limit"] else 0)
        self.center_card_pos = (0, 0)
        self.player_positions = [(0, 0) for _ in self.players]
        self.lock_until = 0
        self.state = "PLAYING"

    def _names(self):
        names = list(self.config["player_names"])
        while len(names) < 2:
            names.append(f"Jugador {len(names) + 1}")
        return names

    def _new_game(self):
        self.mode = "single"
        self._apply_card_scale()
        self.deck = Deck()
        self.deck.shuffle()
        self.center_card = self.deck.draw_card()
        self.players = [Player(self._names()[0], is_human=True)]
        self.players[0].color = PLAYER1_COLOR
        for player in self.players:
            card = self.deck.draw_card()
            if card:
                player.add_card(card)
        self._reset_state()

    def _new_local_game(self):
        self.mode = "local"
        self._apply_card_scale()
        self.deck = Deck()
        self.deck.shuffle()
        self.center_card = self.deck.draw_card()
        names = self._names()
        self.players = [
            Player(names[0], is_human=True),
            Player(names[1], is_human=True),
        ]
        self.players[0].color = PLAYER1_COLOR
        self.players[1].color = PLAYER2_COLOR
        for player in self.players:
            card = self.deck.draw_card()
            if card:
                player.add_card(card)
        self._reset_state()

    def _restart_game(self):
        if self.mode == "local":
            self._new_local_game()
        else:
            self._new_game()

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
                self.screen = pygame.display.set_mode((self.w, self.h), self._window_flags())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

    def handle_key(self, key):
        if self.state == "SETTINGS":
            self._handle_settings_key(key)
            return
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
            self._restart_game()
        elif self.state == "PLAYING" and self.mode == "local" and not self.game_over:
            self._handle_local_input(pygame.key.name(key))

    def _handle_settings_key(self, key):
        rows = self.settings_rows
        if self.editing is not None:
            row = rows[self.settings_index]
            if key == pygame.K_ESCAPE or key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self.editing = None
            elif key == pygame.K_BACKSPACE:
                names = list(self.config["player_names"])
                current = names[row["index"]][:-1]
                names[row["index"]] = current
                self.config["player_names"] = names
                self.config.save()
            else:
                name = pygame.key.name(key)
                if len(name) == 1 and name.isprintable():
                    names = list(self.config["player_names"])
                    current = names[row["index"]]
                    if len(current) < 12:
                        names[row["index"]] = current + name
                        self.config["player_names"] = names
                        self.config.save()
            return

        if key in (pygame.K_UP, pygame.K_w):
            self.settings_index = (self.settings_index - 1) % len(rows)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.settings_index = (self.settings_index + 1) % len(rows)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self._change_setting(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._change_setting(1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            row = rows[self.settings_index]
            if row["type"] == "text":
                self.editing = row["key"]
        elif key == pygame.K_ESCAPE:
            self.state = "MENU"

    def _change_setting(self, delta):
        row = self.settings_rows[self.settings_index]
        if row["type"] != "choice":
            return
        values = row["values"]
        current = self.config[row["key"]]
        try:
            idx = values.index(current)
        except ValueError:
            idx = 0
        idx = (idx + delta) % len(values)
        self.config[row["key"]] = values[idx]
        apply = row.get("apply")
        if apply:
            apply()
        self.config.save()

    def _handle_local_input(self, key_name):
        if not key_name:
            return
        key_name = key_name.upper()
        if pygame.time.get_ticks() < self.lock_until:
            return
        for p_idx, player in enumerate(self.players):
            if not player.hand:
                continue
            card = player.hand[0]
            hit = card.get_symbol_by_key(key_name)
            if hit:
                sym, index = hit
                rel_x, rel_y, _ = card._symbol_positions[index]
                px, py = self.player_positions[p_idx]
                pos = (px + rel_x, py + rel_y)
                if sym in self.center_card.symbols:
                    self._on_correct(player, card, index, pos)
                else:
                    self._on_incorrect(player, index, pos)
                return

    def update(self):
        if self.state == "PLAYING" and not self.game_over:
            limit = self.config["time_limit"]
            if limit > 0:
                elapsed = (pygame.time.get_ticks() - self.game_start) / 1000
                self.time_left = max(0.0, limit - elapsed)
                if self.time_left <= 0:
                    self._end_game()

    def handle_click(self, pos):
        if self.state == "SETTINGS":
            for index, rect in enumerate(self.settings_rects):
                if rect.collidepoint(pos):
                    self.settings_index = index
                    return
            return
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
        if self.mode == "local" and pygame.time.get_ticks() < self.lock_until:
            return
        for p_idx, player in enumerate(self.players):
            if not player.hand:
                continue
            card = player.hand[0]
            px, py = self.player_positions[p_idx]
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
                return

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
        if self.mode == "local":
            self.lock_until = pygame.time.get_ticks() + self.config["input_lock_ms"]
            self.show_message(f"{player.name}: acerto!", player.color)
        else:
            self.show_message("Coincidencia!", ACCENT_SUCCESS)

    def _on_incorrect(self, player, index=0, pos=(0, 0)):
        penalty = self.config["miss_penalty"]
        if penalty != "none":
            player.incorrect += 1
            if penalty == "strong" and player.score > 0:
                player.score -= 1
        self._add_feedback("incorrect", pos)
        if self.config["hint_on_error"]:
            card = player.hand[0]
            if card:
                p_idx = self.players.index(player)
                if p_idx < len(self.player_positions):
                    px, py = self.player_positions[p_idx]
                    for sym, rel in zip(card.symbols, card._symbol_positions):
                        if sym in self.center_card.symbols:
                            hint_pos = (px + rel[0], py + rel[1])
                            self._add_feedback("hint", hint_pos)
                            break
        if self.mode == "local":
            self.show_message(f"{player.name}: no coincide!", ACCENT_ERROR)
        else:
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
        elif self.state == "SETTINGS":
            self._render_settings(screen)
        else:
            self._render_game(screen)
        pygame.display.flip()

    def _render_settings(self, screen):
        screen.fill(BG_COLOR)
        title_font = load_font(FONT_SIZE_TITLE)
        label_font = load_font(22)
        value_font = load_font(FONT_SIZE_MENU)
        hint_font = load_font(16)

        center_x = self.w // 2

        title = title_font.render("CONFIGURACION", True, ACCENT_PRIMARY)
        screen.blit(title, title.get_rect(center=(center_x, 80)))

        row_h = value_font.get_height() + 26
        start_y = 150

        self.settings_rects = []
        for index, row in enumerate(self.settings_rows):
            selected = index == self.settings_index
            label_color = TEXT_SECONDARY
            rendered_label = label_font.render(row["label"], True, label_color)

            if row["type"] == "text":
                names = self.config["player_names"]
                value = str(names[row["index"]])
                if self.editing is not None and index == self.settings_index:
                    if (pygame.time.get_ticks() // 500) % 2 == 0:
                        value += "_"
                    value_color = ACCENT_WARNING
                else:
                    value_color = TEXT_PRIMARY
            else:
                values = row["values"]
                labels = row["labels"]
                try:
                    idx = values.index(self.config[row["key"]])
                except ValueError:
                    idx = 0
                value = labels[idx]
                value_color = ACCENT_PRIMARY

            label_rect = rendered_label.get_rect(
                midleft=(center_x - 240, start_y + index * row_h))

            row_bg = pygame.Rect(center_x - 270, start_y + index * row_h - row_h // 2,
                                 540, row_h)
            if selected:
                pygame.draw.rect(screen, BG_PANEL, row_bg, border_radius=10)
                pygame.draw.rect(screen, ACCENT_PRIMARY, row_bg, 2, border_radius=10)

            screen.blit(rendered_label, label_rect)

            rendered_value = value_font.render(value, True, value_color)
            value_rect = rendered_value.get_rect(
                midright=(center_x + 240, start_y + index * row_h))
            screen.blit(rendered_value, value_rect)

            self.settings_rects.append(row_bg)

        if self.editing is not None:
            hints = "Escribiendo nombre...  Enter/Esc: terminar"
        else:
            hints = "Arriba/Abajo o W/S: mover   Izq/Der o A/D: cambiar   Enter: editar nombre   Esc: volver"
        hint = hint_font.render(hints, True, TEXT_MUTED)
        screen.blit(hint, hint.get_rect(center=(center_x, self.h - 50)))

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
            py = cy + CARD_HEIGHT + 70
            if self.mode == "local":
                left_cx = play_left + int(play_w * 0.28)
                right_cx = play_left + int(play_w * 0.72)
                self.player_positions = [
                    (left_cx - CARD_WIDTH // 2, py),
                    (right_cx - CARD_WIDTH // 2, py),
                ]
            else:
                self.player_positions = [(cx, py)]
            for p_idx, player in enumerate(self.players):
                if player.hand and p_idx < len(self.player_positions):
                    card = player.hand[0]
                    if self.mode == "local":
                        card.set_key_labels(P1_KEYS if p_idx == 0 else P2_KEYS)
                    else:
                        card.set_key_labels([])
                    px, pyy = self.player_positions[p_idx]
                    card.draw(screen, px, pyy)
        self._draw_feedback(screen)
        self._draw_message(screen)
        if self.game_over:
            self._draw_game_over(screen)
        pygame.display.flip()

    def _draw_timer(self, screen):
        if self.config["time_limit"] <= 0 or self.time_left <= 0:
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
        ratio = max(0.0, min(1.0, self.time_left / self.config["time_limit"]))
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

        if self.mode == "local":

            def player_section(player, base_y):
                color = player.color
                center_text(screen, player.name, base_y, label_font, color)
                center_text(screen, str(player.score), base_y + 32, value_font, TEXT_PRIMARY)
                center_text(screen, "Correctas", base_y + 70, label_font, TEXT_SECONDARY)
                center_text(screen, str(player.correct), base_y + 94, value_font, ACCENT_SUCCESS)
                center_text(screen, "Fallos", base_y + 126, label_font, TEXT_SECONDARY)
                center_text(screen, str(player.incorrect), base_y + 150, value_font, ACCENT_ERROR)
                pygame.draw.line(screen, BORDER, (20, base_y + 170),
                                 (SCORE_PANEL_WIDTH - 20, base_y + 170), 1)

            player_section(self.players[0], 100)
            player_section(self.players[1], 320)
            center_text(screen, "Mazo", self.h - 130, label_font, TEXT_SECONDARY)
            center_text(screen, str(self.deck.remaining()), self.h - 100, value_font, TEXT_PRIMARY)
            return

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
        gap_bottom = self.player_positions[0][1] if self.player_positions else 0
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
        font = load_font(26)
        label_font = load_font(20)
        line_h = font.get_height() + 10
        center_x = SCORE_PANEL_WIDTH + (self.w - SCORE_PANEL_WIDTH) // 2

        if self.mode == "local":
            max_score = max(p.score for p in self.players)
            winners = [p for p in self.players if p.score == max_score]
            min_fallos = min(p.incorrect for p in winners)
            winners = [p for p in winners if p.incorrect == min_fallos]
            if len(winners) == 1:
                title = f"GANADOR: {winners[0].name}"
                title_color = winners[0].color
            else:
                title = "EMPATE"
                title_color = ACCENT_WARNING

            lines = [f"{p.name}: {p.score} pts  (C:{p.correct}  F:{p.incorrect})"
                     for p in self.players]
            start_y = self.h // 2 - (line_h * (len(lines) + 1)) // 2

            rendered = font.render(title, True, title_color)
            screen.blit(rendered, rendered.get_rect(center=(center_x, start_y)))
            for i, line in enumerate(lines):
                text = label_font.render(line, True, TEXT_PRIMARY)
                rect = text.get_rect(center=(center_x, start_y + (i + 1) * line_h))
                screen.blit(text, rect)

            hint_y = start_y + (len(lines) + 1) * line_h + 10
            hint = label_font.render("R: reiniciar   Esc: menu", True, TEXT_MUTED)
            screen.blit(hint, hint.get_rect(center=(center_x, hint_y)))
            return

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
        start_y = self.h // 2 - (line_h * len(lines)) // 2
        for i, line in enumerate(lines):
            color = TEXT_PRIMARY
            if i == 0:
                color = ACCENT_PRIMARY
            rendered = font.render(line, True, color)
            rect = rendered.get_rect(center=(center_x, start_y + i * line_h))
            screen.blit(rendered, rect)