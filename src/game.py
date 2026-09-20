import math
import sys

import pygame

from card import Card
from constants import *
from config import Config, DEFAULT_CONFIG, normalize_key
from deck import Deck
from fonts import load_font
from player import Player
from sound import SoundManager


P1_KEYS = list(DEFAULT_CONFIG["p1_keys"])
P2_KEYS = list(DEFAULT_CONFIG["p2_keys"])
INPUT_LOCK_MS = 300
INTRO_NUMBER_MS = 700
INTRO_GO_MS = 2100
INTRO_END_MS = 2700
INTRO_LOOP_FADE_MS = 2000
INTRO_LOOP_OVERLAP_MS = 1000
INTRO_ENTRY_MS = 550
SYMBOL_SIZES = {"small": 40, "normal": 50, "large": 60}

_KEY_LABEL_SHORTHAND = {
    "space": "SPACE", "left shift": "LSHIFT", "right shift": "RSHIFT",
    "left ctrl": "LCTRL", "right ctrl": "RCTRL", "left alt": "LALT",
    "right alt": "RALT", "left meta": "LMETA", "right meta": "RMETA",
    "caps lock": "CAPS", "backspace": "BKSP", "delete": "DEL",
    "insert": "INS", "pageup": "PGUP", "pagedown": "PGDN",
    "home": "HOME", "end": "END", "return": "ENTER", "kpenter": "ENTER",
    "kp0": "0", "kp1": "1", "kp2": "2", "kp3": "3", "kp4": "4",
    "kp5": "5", "kp6": "6", "kp7": "7", "kp8": "8", "kp9": "9",
}


class Game:
    def __init__(self):
        self.config = Config()
        self.w, self.h = SCREEN_WIDTH, SCREEN_HEIGHT
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode((self.w, self.h), self._window_flags())
        pygame.display.set_caption("Dobble")
        self.clock = pygame.time.Clock()
        self.running = True
        self.sound = SoundManager()
        self.sound.play_music("lobby")
        if self.config["fullscreen"]:
            self._apply_fullscreen()

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
        self.settings_wheel = 0.0
        self.editing = None
        self.editing_step = 0
        self.modal = None
        self.modal_btn_rects = []
        self.game_over_rects = []
        self._game_over_rects_local = []
        self.game_over_start = 0
        self._game_over_backdrop = None
        self._name_index = 0
        self._name_before = None
        self._keys_backup = None
        self.settings_key_msg = ""
        self.settings_key_msg_end = 0
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
            {"label": "Teclas Jugador 1", "type": "keys", "key": "p1_keys"},
            {"label": "Teclas Jugador 2", "type": "keys", "key": "p2_keys"},
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
            self.screen = pygame.display.set_mode((self.w, self.h), self._window_flags())
        except pygame.error:
            self.config["fullscreen"] = not self.config["fullscreen"]
            self.screen = pygame.display.set_mode((self.w, self.h), self._window_flags())
            return
        if self.config["fullscreen"]:
            self.windowed_size = (self.w, self.h)
            self.w, self.h = self.screen.get_size()
        else:
            self.w, self.h = self.windowed_size

    def _apply_card_scale(self):
        Card.set_layout(symbol_size=SYMBOL_SIZES.get(self.config["card_scale"], 50))

    def _open_settings(self):
        self.state = "SETTINGS"
        self.settings_index = 0
        self.settings_wheel = 0.0
        self.editing = None
        self.editing_step = 0
        self.modal = None
        self.modal_btn_rects = []
        self._name_index = 0
        self._name_before = None
        self._keys_backup = None
        self.settings_key_msg = ""
        self.settings_key_msg_end = 0

    def _reset_state(self):
        self.game_over = False
        self.game_over_rects = []
        self._game_over_backdrop = None
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
        self.intro = True
        self.intro_start = pygame.time.get_ticks()
        self.intro_t = 0.0
        self.intro_tick = -1
        self.intro_go = False
        self.sound.fade_out_music(400)

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
                if not self.config["fullscreen"]:
                    self.w, self.h = event.w, event.h
                    self.windowed_size = (self.w, self.h)
                    self.screen = pygame.display.set_mode((self.w, self.h), self._window_flags())
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
            elif (event.type == pygame.MOUSEBUTTONDOWN and
                  event.button in (4, 5) and self.state == "SETTINGS"
                  and self.modal is None):
                delta = -1 if event.button == 4 else 1
                self.settings_index = (self.settings_index + delta) % len(self.settings_rows)
                self.sound.play_effect("navigate")
            elif event.type == pygame.KEYDOWN:
                self.handle_key(event.key)

    def handle_key(self, key):
        if self.state == "SETTINGS":
            self._handle_settings_key(key)
            return
        if self.state == "MENU":
            if key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                self.sound.play_effect("navigate")
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                self.sound.play_effect("navigate")
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                self.sound.play_effect("select")
                _, callback = self.menu_options[self.menu_index]
                callback()
            elif key == pygame.K_ESCAPE:
                self.running = False
        elif key == pygame.K_ESCAPE:
            self._go_to_menu()
        elif key == pygame.K_r and self.game_over:
            self._restart_game()
        elif self.state == "PLAYING" and self.mode == "local" and not self.game_over:
            self._handle_local_input(pygame.key.name(key))

    def _go_to_menu(self):
        self.state = "MENU"
        self.game_over = False
        self.game_over_rects = []
        self._game_over_backdrop = None
        self.sound.stop_music()
        self.sound.play_music("lobby")

    def _handle_settings_key(self, key):
        rows = self.settings_rows

        if self.modal == "keys":
            if key == pygame.K_ESCAPE:
                self._cancel_key_edit()
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._accept_key_edit()
            else:
                self._assign_key(pygame.key.name(key))
            return

        if self.modal == "name":
            if key == pygame.K_ESCAPE:
                self._cancel_name_edit()
            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._accept_name_edit()
            elif key == pygame.K_BACKSPACE:
                names = list(self.config["player_names"])
                current = names[self._name_index][:-1]
                names[self._name_index] = current
                self.config["player_names"] = names
            else:
                name = pygame.key.name(key)
                if len(name) == 1 and name.isprintable():
                    names = list(self.config["player_names"])
                    current = names[self._name_index]
                    if len(current) < 12:
                        names[self._name_index] = current + name
                        self.config["player_names"] = names
            return

        row = rows[self.settings_index]

        if key in (pygame.K_UP, pygame.K_w):
            self.settings_index = (self.settings_index - 1) % len(rows)
            self.sound.play_effect("navigate")
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.settings_index = (self.settings_index + 1) % len(rows)
            self.sound.play_effect("navigate")
        elif key in (pygame.K_LEFT, pygame.K_a):
            self._change_setting(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._change_setting(1)
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.sound.play_effect("select")
            if row["type"] == "text":
                self.editing = "player_names"
                self.modal = "name"
                self._name_index = row["index"]
                self._name_before = list(self.config["player_names"])
            elif row["type"] == "keys":
                self.editing = row["key"]
                self.modal = "keys"
                self.editing_step = 0
                self._keys_backup = list(self.config[row["key"]])
                self.config[row["key"]] = list(self.config[row["key"]])
        elif key == pygame.K_ESCAPE:
            self._go_to_menu()

    def _other_player_keys(self, key_name):
        other = "p2_keys" if key_name == "p1_keys" else "p1_keys"
        return [k.upper() for k in self.config[other] if k]

    def _assign_key(self, coded_name):
        row = self.settings_rows[self.settings_index]
        key_name = row["key"]
        new_key = normalize_key(coded_name)
        if not new_key:
            return
        keys = self.config[key_name]
        bound = [k.upper() for k in keys[:self.editing_step] if k]
        if (new_key in bound or new_key in self._other_player_keys(key_name)):
            self.settings_key_msg = "Tecla ya usada"
            self.settings_key_msg_end = pygame.time.get_ticks() + 1800
            self.sound.play_effect("error")
            return
        keys[self.editing_step] = new_key
        self.config[key_name] = keys
        self.editing_step += 1
        self.sound.play_effect("navigate")
        if self.editing_step >= 8:
            self._accept_key_edit()

    def _accept_key_edit(self):
        self.config.save()
        self.modal = None
        self.editing = None
        self.editing_step = 0
        self._keys_backup = None
        self.sound.play_effect("select")

    def _cancel_key_edit(self):
        key_name = self.editing
        if self._keys_backup is not None:
            self.config[key_name] = self._keys_backup
        self.modal = None
        self.editing = None
        self.editing_step = 0
        self.settings_key_msg = ""
        self._keys_backup = None
        self.sound.play_effect("select")

    def _accept_name_edit(self):
        self.config.save()
        self.modal = None
        self.editing = None
        self._name_before = None
        self.sound.play_effect("select")

    def _cancel_name_edit(self):
        if self._name_before is not None:
            self.config["player_names"] = self._name_before
        self.modal = None
        self.editing = None
        self._name_before = None
        self.sound.play_effect("select")

    def _handle_modal_click(self, pos):
        for action, rect in self.modal_btn_rects:
            if rect.collidepoint(pos):
                if self.modal == "name":
                    if action == "accept":
                        self._accept_name_edit()
                    else:
                        self._cancel_name_edit()
                elif self.modal == "keys":
                    if action == "accept":
                        self._accept_key_edit()
                    else:
                        self._cancel_key_edit()
                break

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
        self.sound.play_effect("navigate")

    def _handle_local_input(self, key_name):
        if not key_name:
            return
        key_name = normalize_key(key_name)
        if not key_name:
            return
        if pygame.time.get_ticks() < self.lock_until:
            return
        if self.intro:
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
        self.sound.update()
        if self.state == "SETTINGS":
            n = len(self.settings_rows)
            target = self.settings_index + n * round(
                (self.settings_wheel - self.settings_index) / n)
            self.settings_wheel += (target - self.settings_wheel) * 0.18
            if abs(target - self.settings_wheel) < 0.01:
                self.settings_wheel = float(target)
                self.settings_index = target % n
        if self.state == "PLAYING" and not self.game_over:
            if self.intro:
                now = pygame.time.get_ticks()
                self.intro_t = (now - self.intro_start) / 1000.0
                idx = int(self.intro_t * 1000 / INTRO_NUMBER_MS)
                if idx != self.intro_tick and idx < 3:
                    self.intro_tick = idx
                    self.sound.play_effect("coincidence", volume=0.18)
                if not self.intro_go and now - self.intro_start >= INTRO_GO_MS:
                    self.intro_go = True
                    self.sound.play_effect("start")
                    jingle_ms = self.sound.effect_length("start") * 1000
                    delay = max(0.0, jingle_ms - INTRO_LOOP_OVERLAP_MS)
                    self.sound.fade_in_music(
                        "game", fade_ms=INTRO_LOOP_FADE_MS, delay_ms=delay)
                if now - self.intro_start >= INTRO_END_MS:
                    self.intro = False
                    self.game_start = now
            else:
                limit = self.config["time_limit"]
                if limit > 0:
                    elapsed = (pygame.time.get_ticks() - self.game_start) / 1000
                    self.time_left = max(0.0, limit - elapsed)
                    if self.time_left <= 0:
                        self._end_game()

    def handle_click(self, pos):
        if self.state == "SETTINGS":
            if self.modal is not None:
                self._handle_modal_click(pos)
                return
            for index, rect in self.settings_rects:
                if rect and rect.collidepoint(pos):
                    self.settings_index = index
                    self.sound.play_effect("navigate")
                    return
            return
        if self.state == "MENU":
            for index, rect in enumerate(self.menu_rects):
                if rect.collidepoint(pos):
                    self.menu_index = index
                    self.sound.play_effect("select")
                    _, callback = self.menu_options[index]
                    callback()
                    return
            return
        if self.game_over:
            for action, rect in self.game_over_rects:
                if rect.collidepoint(pos):
                    self.sound.play_effect("select")
                    if action == "restart":
                        self._restart_game()
                    else:
                        self._go_to_menu()
                    return
            return
        if self.intro:
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
        self.sound.play_effect("coincidence")
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
        self.sound.play_effect("error")
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
        self.game_over_start = pygame.time.get_ticks()
        self.game_over_rects = []
        self._game_over_backdrop = None
        self.message = "FIN DE PARTIDA"
        self.message_color = ACCENT_WARNING
        self.message_end = pygame.time.get_ticks() + 60000
        self.sound.stop_music()
        self.sound.play_effect("game_over")

    def show_message(self, text, color):
        self.message = text
        self.message_color = color
        self.message_end = pygame.time.get_ticks() + 1600

    def _breath_scale(self, amount=0.03, period=2.2):
        """Factor de escala (aprox 0.97-1.03) para la animacion de respiracion."""
        t = pygame.time.get_ticks() / 1000.0
        return 1.0 + amount * math.sin(t * math.tau / period)

    def _fit_scaled(self, surface, scale):
        """Devuelve la superficie escalada por `scale` (o la misma si no cambia)."""
        w, h = surface.get_size()
        if w == 0 or h == 0:
            return surface
        sw = max(1, int(w * scale))
        sh = max(1, int(h * scale))
        if (sw, sh) == (w, h):
            return surface
        return pygame.transform.smoothscale(surface, (sw, sh))

    def _blit_breathing(self, surface, text_surf, rect, scale):
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
        if self.modal is not None:
            surface = pygame.Surface((self.w, self.h))
            self._draw_settings_screen(surface)
            screen.blit(self._blur_backdrop(surface), (0, 0))
            self._draw_modal(screen)
        else:
            self._draw_settings_screen(screen)

    def _blur_backdrop(self, surface):
        w, h = surface.get_size()
        small = pygame.transform.smoothscale(
            surface, (max(1, w // 8), max(1, h // 8)))
        blurred = pygame.transform.smoothscale(small, (w, h))
        veil = pygame.Surface((w, h), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 130))
        blurred.blit(veil, (0, 0))
        return blurred

    def _draw_settings_screen(self, screen):
        screen.fill(BG_COLOR)
        title_font = load_font(FONT_SIZE_TITLE)

        center_x = self.w // 2
        editing = self.modal is None and self.editing
        n = len(self.settings_rows)

        title = title_font.render("CONFIGURACION", True, ACCENT_PRIMARY)
        screen.blit(title, title.get_rect(center=(center_x, 80)))

        # --- RUEDA VERTICAL ---
        # Las opciones giran como una rueda: la fila del centro se agranda y
        # las de los lados se ven mas pequeñas y apagadas; la seleccionada
        # ademas respira. Todo el texto va centrado en la pantalla.
        center_y = self.h // 2 + 8
        pitch = 96
        decay = 0.82
        center_scale = 1.12

        wheel = self.settings_wheel
        base = math.floor(wheel)
        frac = wheel - base

        self.settings_rects = []
        for k in range(-7, 8):
            idx = (base + k) % n
            dz = k - frac
            y = center_y + dz * pitch
            if y < 128 or y > self.h - 84:
                continue
            scale = center_scale * (decay ** abs(dz))
            if scale < 0.5:
                continue
            fade = max(0.0, 1.0 - abs(dz) * 0.22)
            if fade <= 0.05:
                continue

            row = self.settings_rows[idx]
            selected = idx == int(round(wheel)) % n
            is_edited = editing is not None and idx == self.settings_index

            _, rendered_label = self._render_fitting_text(
                row["label"], [22, 20, 18, 16, 14], int(self.w * 0.7),
                TEXT_SECONDARY)

            if row["type"] == "text":
                names = self.config["player_names"]
                value = str(names[row["index"]])
                if is_edited:
                    if (pygame.time.get_ticks() // 500) % 2 == 0:
                        value += "_"
                    value_color = ACCENT_WARNING
                else:
                    value_color = TEXT_PRIMARY
            elif row["type"] == "keys":
                keys = list(self.config[row["key"]])
                parts = []
                for i, kk in enumerate(keys):
                    show = kk.upper() if kk else "-"
                    if editing == row["key"] and i == self.editing_step:
                        cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
                        show += cursor
                    parts.append(show)
                value = "  ".join(parts)
                value_color = ACCENT_WARNING if editing == row["key"] else ACCENT_PRIMARY
            else:
                values = row["values"]
                labels = row["labels"]
                try:
                    v_idx = values.index(self.config[row["key"]])
                except ValueError:
                    v_idx = 0
                value = labels[v_idx]
                value_color = ACCENT_PRIMARY

            sizes_keys = [FONT_SIZE_GAME, 22, 19, 16, 13]
            sizes_value = [FONT_SIZE_GAME, 22, 19, 16]
            _, rendered_value = self._render_fitting_text(
                value, sizes_keys if row["type"] == "keys" else sizes_value,
                int(self.w * 0.7), value_color)

            v_scale = scale * self._breath_scale() if selected else scale
            show_label = self._fit_scaled(rendered_label, scale)
            show_value = self._fit_scaled(rendered_value, v_scale)

            lh = show_label.get_height()
            vh = show_value.get_height()
            label_rect = show_label.get_rect(midbottom=(center_x, y - 4))
            value_rect = show_value.get_rect(midtop=(center_x, y + 4))

            alpha = int(255 * fade)
            if alpha < 255:
                show_label.set_alpha(alpha)
                show_value.set_alpha(alpha)

            screen.blit(show_label, label_rect)
            screen.blit(show_value, value_rect)

            block_w = max(show_label.get_width(), show_value.get_width()) + 40
            click_rect = pygame.Rect(0, 0, block_w, lh + vh + 8)
            click_rect.center = (center_x, y)
            self.settings_rects.append((idx, click_rect))

        hints = "Arriba/Abajo o W/S: mover   Izq/Der o A/D: cambiar   Enter: editar nombre o teclas   Esc: volver"
        _, hint = self._render_fitting_text(
            hints, [16, 15, 14, 13, 12, 11], self.w - 40, TEXT_MUTED)
        screen.blit(hint, hint.get_rect(center=(center_x, self.h - 50)))

    def _draw_modal(self, screen):
        if self.modal == "name":
            self._draw_modal_name(screen)
        elif self.modal == "keys":
            self._draw_modal_keys(screen)

    def _draw_modal_panel(self, screen, w, h):
        rect = pygame.Rect((self.w - w) // 2, (self.h - h) // 2, w, h)
        panel_color = tuple(min(255, int(c * 1.08)) for c in BG_PANEL)
        pygame.draw.rect(screen, panel_color, rect, border_radius=16)
        pygame.draw.rect(screen, ACCENT_PRIMARY, rect, 3, border_radius=16)
        return rect

    def _draw_modal_buttons(self, screen, panel, labels=("Cancelar", "Aceptar")):
        self.modal_btn_rects = []
        btn_w, btn_h = 170, 46
        gap = 24
        total = btn_w * 2 + gap
        x0 = panel.centerx - total // 2
        by = panel.bottom - btn_h - 18
        actions = ("cancel", "accept")
        for i, (label, action) in enumerate(zip(labels, actions)):
            rect = pygame.Rect(x0 + i * (btn_w + gap), by, btn_w, btn_h)
            border = ACCENT_ERROR if action == "cancel" else ACCENT_SUCCESS
            pygame.draw.rect(screen, BG_SECONDARY, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, 2, border_radius=10)
            font, label_surf = self._render_fitting_text(
                label, [FONT_SIZE_GAME, 22, 19, 16], btn_w - 16, TEXT_PRIMARY)
            screen.blit(label_surf, label_surf.get_rect(center=rect.center))
            self.modal_btn_rects.append((action, rect))

    def _key_display_name(self, key):
        if not key:
            return "-"
        value = key.upper()
        return _KEY_LABEL_SHORTHAND.get(key.lower().replace(" ", ""), value)

    def _render_fitting_text(self, text, sizes, max_w, color):
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

    def _draw_modal_keys(self, screen):
        panel = self._draw_modal_panel(screen, 620, 440)
        title_font = load_font(30)
        hint_font = load_font(16)
        player_num = 1 if self.editing == "p1_keys" else 2
        title = title_font.render(f"Teclas Jugador {player_num}", True, ACCENT_PRIMARY)
        screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + 44)))

        keys = self.config[self.editing]
        cell = 56
        row_sep = cell + 18
        top_y = panel.top + 100
        rows_layout = [
            (0, [-cell, 0, cell]),
            (1, [-cell // 2, cell // 2]),
            (2, [-cell, 0, cell]),
        ]
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        slot_counter = 0
        for row_idx, cols in rows_layout:
            y = top_y + row_idx * row_sep
            for cx_off in cols:
                rect = pygame.Rect(0, 0, cell, cell)
                rect.center = (panel.centerx + cx_off, y)
                pygame.draw.rect(screen, BG_SECONDARY, rect, border_radius=12)
                border = BORDER
                if slot_counter == self.editing_step:
                    border = ACCENT_WARNING if blink else ACCENT_PRIMARY
                pygame.draw.rect(screen, border, rect,
                                 3 if slot_counter == self.editing_step else 2,
                                 border_radius=12)
                key = keys[slot_counter]
                label = self._key_display_name(key)
                font, key_surf = self._render_fitting_text(
                    label, [28, 24, 20, 16, 13], cell - 14, TEXT_PRIMARY)
                screen.blit(key_surf, key_surf.get_rect(center=rect.center))
                slot_counter += 1

        pos = self.editing_step + 1
        progress = hint_font.render(
            f"Tecla {pos}/8: pulsa una tecla para asignarla", True, ACCENT_WARNING)
        screen.blit(progress, progress.get_rect(center=(panel.centerx, panel.top + 322)))

        if self.settings_key_msg and pygame.time.get_ticks() < self.settings_key_msg_end:
            msg = hint_font.render(self.settings_key_msg, True, ACCENT_ERROR)
            screen.blit(msg, msg.get_rect(center=(panel.centerx, panel.top + 352)))

        esc_note = hint_font.render("Esc: cancelar   Enter: aceptar", True, TEXT_MUTED)
        screen.blit(esc_note, esc_note.get_rect(center=(panel.centerx, panel.bottom - 58)))

    def _draw_modal_name(self, screen):
        panel = self._draw_modal_panel(screen, 560, 250)
        title_font = load_font(30)
        name_font = load_font(FONT_SIZE_MESSAGE)
        hint_font = load_font(16)
        player_num = self._name_index + 1
        title = title_font.render(f"Nombre Jugador {player_num}", True, ACCENT_PRIMARY)
        title_rect = title.get_rect(center=(panel.centerx, panel.top + 40))
        screen.blit(title, title_rect)
        pygame.draw.line(screen, ACCENT_PRIMARY, (panel.left + 40, title_rect.bottom + 16),
                         (panel.right - 60, title_rect.bottom + 16), 2)

        name = self.config["player_names"][self._name_index]
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            name += "_"
        label = "Escribe el nombre:"
        label_surf = hint_font.render(label, True, TEXT_SECONDARY)
        screen.blit(label_surf, label_surf.get_rect(center=(panel.centerx, panel.top + 92)))

        name_font, name_surf = self._render_fitting_text(
            name, [FONT_SIZE_MESSAGE, 30, 24, 20, 16], panel.w - 120, ACCENT_WARNING)
        text_rect = name_surf.get_rect(center=(panel.centerx, panel.top + 138))
        box = text_rect.inflate(40, 18)
        pygame.draw.rect(screen, BG_SECONDARY, box, border_radius=10)
        pygame.draw.rect(screen, BORDER, box, 2, border_radius=10)
        screen.blit(name_surf, text_rect)

        # --- SIN BOTONES (fix: Cancelar/Aceptar tapaban el texto de atras) ---
        # Antes los botones (rect 170x46 al pie del panel) se superponian en Y
        # con las instrucciones de teclado (y con el texto del campo cuando el
        # nombre se salia del cuadro). Ahora no se dibujan botones: la casilla
        # del nombre y las instrucciones ("Enter: aceptar   Esc: cancelar") son
        # los unicos elementos del modal, asi nada se pisa entre si.
        hint = hint_font.render("Enter: aceptar   Esc: cancelar", True, TEXT_MUTED)
        screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - 60)))

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
            _, rendered = self._render_fitting_text(
                label, [FONT_SIZE_MENU, 32, 28, 24, 20, 16],
                min(int(self.w * 0.7), 700), color)
            rect = rendered.get_rect(center=(center_x, start_y + index * option_h))
            if selected:
                self._blit_breathing(screen, rendered, rect, self._breath_scale())
            else:
                screen.blit(rendered, rect)
            self.menu_rects.append(rect)

        hints = "Arriba/Abajo o W/S: mover   Enter/Espacio: elegir   Esc: salir"
        _, hint = self._render_fitting_text(
            hints, [16, 15, 14, 13, 12, 11], self.w - 40, TEXT_MUTED)
        screen.blit(hint, hint.get_rect(center=(center_x, self.h - 50)))

        if self.menu_msg and pygame.time.get_ticks() < self.menu_msg_end:
            _, msg = self._render_fitting_text(
                self.menu_msg, [FONT_SIZE_SMALL, 18, 16, 14], self.w - 40, ACCENT_WARNING)
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
                        card.set_key_labels(self.config["p1_keys"] if p_idx == 0 else self.config["p2_keys"])
                    else:
                        card.set_key_labels([])
            if self.intro:
                self._draw_intro_cards(screen)
            else:
                self.center_card.draw(screen, cx, cy)
                for p_idx, player in enumerate(self.players):
                    if player.hand and p_idx < len(self.player_positions):
                        player.hand[0].draw(screen, *self.player_positions[p_idx])
            if self.intro:
                self._draw_intro_effects(screen)
        self._draw_feedback(screen)
        self._draw_message(screen)
        if self.game_over:
            self._draw_game_over(screen)
        pygame.display.flip()

    @staticmethod
    def _ease_out_cubic(t):
        t = max(0.0, min(1.0, t))
        return 1.0 - (1.0 - t) ** 3

    @staticmethod
    def _ease_out_back(t):
        t = max(0.0, min(1.0, t))
        c1 = 1.70158
        c3 = c1 + 1.0
        t -= 1.0
        return 1.0 + c3 * t ** 3 + c1 * t ** 2

    def _blit_intro_card(self, screen, card, final_center, offset, angle0, e):
        scale = max(0.12, 0.12 + 0.88 * e)
        w = max(2, int(CARD_WIDTH * scale))
        h = max(2, int(CARD_HEIGHT * scale))
        img = pygame.transform.smoothscale(card.to_surface(), (w, h))
        angle = angle0 * (1.0 - e)
        if angle:
            img = pygame.transform.rotate(img, angle)
        x = final_center[0] + int(offset[0] * (1.0 - e))
        y = final_center[1] + int(offset[1] * (1.0 - e))
        screen.blit(img, img.get_rect(center=(x, y)))

    def _draw_intro_cards(self, screen):
        if self.intro_t * 1000 < INTRO_GO_MS:
            return
        local = min(1.0, (self.intro_t * 1000 - INTRO_GO_MS) / INTRO_ENTRY_MS)
        e = self._ease_out_back(local)
        cx, cy = self.center_card_pos
        self._blit_intro_card(
            screen, self.center_card,
            (cx + CARD_WIDTH // 2, cy + CARD_HEIGHT // 2), (0, -150), -14, e)
        if self.mode == "local":
            offsets = [(-330, 130), (330, 130)]
            angles = [12, -12]
        else:
            offsets = [(0, 170)]
            angles = [14]
        for idx, (ox, oy) in enumerate(offsets):
            if idx < len(self.players) and self.players[idx].hand:
                px, pyy = self.player_positions[idx]
                self._blit_intro_card(
                    screen, self.players[idx].hand[0],
                    (px + CARD_WIDTH // 2, pyy + CARD_HEIGHT // 2),
                    (ox, oy), angles[idx], e)

    def _scaled_text(self, text, base_size, scale, color, alpha=255):
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

    def _draw_intro_effects(self, screen):
        t = self.intro_t
        cx, cy = self.center_card_pos
        center = (cx + CARD_WIDTH // 2, cy + CARD_HEIGHT // 2)
        anchor_y = cy + CARD_HEIGHT + 40
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        if t * 1000 < INTRO_GO_MS:
            idx = min(2, int(t * 1000 / INTRO_NUMBER_MS))
            label = ("3", "2", "1")[idx]
            local = (t * 1000 - idx * INTRO_NUMBER_MS) / INTRO_NUMBER_MS
            appear = min(1.0, local * 4.0)
            scale = 1.0 + 0.6 * (1.0 - self._ease_out_cubic(appear))
            alpha = 255
            if local > 0.45:
                alpha = int(255 * max(0.0, 1.0 - (local - 0.45) / 0.25))
            txt = self._scaled_text(label, 130, scale, ACCENT_PRIMARY, alpha)
            overlay.blit(txt, txt.get_rect(center=(center[0], anchor_y)))
        else:
            ring_t = min(1.0, (t * 1000 - INTRO_GO_MS) / 700.0)
            max_r = CARD_WIDTH // 2 + 60
            for rt, color in [(ring_t, ACCENT_PRIMARY),
                              (max(0.0, ring_t - 0.3), ACCENT_SUCCESS)]:
                if rt > 0:
                    radius = int(30 + (max_r - 30) * self._ease_out_cubic(rt))
                    alpha = int(230 * (1.0 - rt))
                    pygame.draw.circle(overlay, (*color, alpha), center, radius, 4)
            go = (t * 1000 - INTRO_GO_MS) / INTRO_ENTRY_MS
            appear = min(1.0, go * 2.2)
            scale = 0.6 + 0.5 * self._ease_out_back(appear)
            alpha = 255
            if go > 0.62:
                alpha = int(255 * max(0.0, 1.0 - (go - 0.62) / 0.08))
            txt = self._scaled_text("¡YA!", 120, scale, ACCENT_SUCCESS, alpha)
            overlay.blit(txt, txt.get_rect(center=(center[0], anchor_y)))
        screen.blit(overlay, (0, 0))

    def _draw_timer(self, screen):
        if self.intro or self.config["time_limit"] <= 0 or self.time_left <= 0:
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
        now = pygame.time.get_ticks()
        elapsed = (now - self.game_over_start) / 1000.0
        enter = min(1.0, elapsed / 0.40)
        panel_scale = 0.74 + 0.26 * self._ease_out_back(enter)

        pw = min(760, self.w - 100)
        ph = 470 if self.mode == "local" else 440
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_color = tuple(min(255, int(c * 1.08)) for c in BG_PANEL)
        bounds = pygame.Rect(0, 0, pw, ph)
        pygame.draw.rect(panel, panel_color, bounds, border_radius=18)
        pygame.draw.rect(panel, ACCENT_PRIMARY, bounds, 3, border_radius=18)

        mx, my = pygame.mouse.get_pos()
        panel_mouse = ((mx - self.w // 2) / panel_scale + pw / 2,
                       (my - self.h // 2) / panel_scale + ph / 2)

        self._game_over_rects_local = []
        self._fill_game_over_panel(panel, elapsed, pw, ph, panel_mouse)

        if self._game_over_backdrop is None:
            self._game_over_backdrop = self._blur_backdrop(screen.copy())
        screen.blit(self._game_over_backdrop, (0, 0))

        sw = max(1, int(pw * panel_scale))
        sh = max(1, int(ph * panel_scale))
        if (sw, sh) == (pw, ph):
            shown = panel
        else:
            shown = pygame.transform.smoothscale(panel, (sw, sh))
        shown_rect = shown.get_rect(center=(self.w // 2, self.h // 2))
        screen.blit(shown, shown_rect)

        self.game_over_rects = [
            (action, pygame.Rect(shown_rect.left + int(r.x * panel_scale),
                                 shown_rect.top + int(r.y * panel_scale),
                                 max(1, int(r.w * panel_scale)),
                                 max(1, int(r.h * panel_scale))))
            for action, r in self._game_over_rects_local
        ]

    def _fill_game_over_panel(self, panel, elapsed, pw, ph, panel_mouse):
        title_font = load_font(34)
        big_font = load_font(60)
        name_font = load_font(24)
        value_font = load_font(30)
        small_font = load_font(16)
        cx = pw // 2
        count = self._ease_out_cubic(min(1.0, elapsed / 0.8))

        if self.mode == "local":
            max_score = max(p.score for p in self.players)
            winners = [p for p in self.players if p.score == max_score]
            min_fallos = min(p.incorrect for p in winners)
            winners = [p for p in winners if p.incorrect == min_fallos]
            if len(winners) == 1:
                title = f"GANADOR: {winners[0].name}"
                title_color = winners[0].color
                winner = winners[0]
            else:
                title = "EMPATE"
                title_color = ACCENT_WARNING
                winner = None

            rendered = self._fit_scaled(title_font.render(title, True, title_color),
                                        self._breath_scale(0.02, 1.6))
            panel.blit(rendered, rendered.get_rect(center=(cx, 58)))
            self._panel_separator(panel, cx, 100, pw)

            for i, player in enumerate(self.players):
                row_y = 178 + i * 96
                is_winner = player is winner
                row = pygame.Rect(46, row_y - 40, pw - 92, 80)
                if is_winner:
                    highlight = tuple(min(255, int(c * 1.14)) for c in BG_PANEL)
                    pygame.draw.rect(panel, highlight, row, border_radius=12)
                    pygame.draw.rect(panel, ACCENT_PRIMARY, row, 2, border_radius=12)
                dot_x = row.x + 34
                pygame.draw.circle(panel, player.color, (dot_x, row_y), 13)
                name_color = player.color if is_winner else TEXT_SECONDARY
                name = player.name or f"Jugador {i + 1}"
                name_s = name_font.render(name, True, name_color)
                panel.blit(name_s, name_s.get_rect(midleft=(dot_x + 26, row_y - 12)))
                detail = small_font.render(
                    f"Correctas {player.correct}   Fallos {player.incorrect}",
                    True, TEXT_MUTED)
                panel.blit(detail, detail.get_rect(midleft=(dot_x + 26, row_y + 16)))
                pts = value_font.render(f"{int(player.score * count)} pts",
                                        True, ACCENT_PRIMARY)
                panel.blit(pts, pts.get_rect(midright=(row.right - 24, row_y + 8)))
                if is_winner:
                    tag = small_font.render("GANADOR", True, ACCENT_PRIMARY)
                    panel.blit(tag, tag.get_rect(midright=(row.right - 24, row_y - 24)))

            self._game_over_buttons(panel, pw, ph, panel_mouse)
            return

        player = self.players[0]
        total = player.correct + player.incorrect
        precision = (player.correct / total * 100) if total else 0.0

        title = self._fit_scaled(
            title_font.render("FIN DE PARTIDA", True, ACCENT_PRIMARY),
            self._breath_scale(0.02, 1.8))
        panel.blit(title, title.get_rect(center=(cx, 58)))
        self._panel_separator(panel, cx, 100, pw)

        big = big_font.render(str(int(player.score * count)), True, ACCENT_PRIMARY)
        panel.blit(big, big.get_rect(center=(cx, 172)))
        label = small_font.render("PUNTOS", True, TEXT_MUTED)
        panel.blit(label, label.get_rect(center=(cx, 216)))

        stats = [
            ("CORRECTAS", int(player.correct * count), ACCENT_SUCCESS),
            ("FALLOS", int(player.incorrect * count), ACCENT_ERROR),
            ("PRECISION", f"{precision * count:.1f}%", TEXT_PRIMARY),
        ]
        for i, (text, value, color) in enumerate(stats):
            sx = int(pw * (0.28 + 0.22 * i))
            shown = value if isinstance(value, str) else str(value)
            v = value_font.render(shown, True, color)
            panel.blit(v, v.get_rect(center=(sx, 292)))
            t = small_font.render(text, True, TEXT_MUTED)
            panel.blit(t, t.get_rect(center=(sx, 328)))

        self._game_over_buttons(panel, pw, ph, panel_mouse)

    def _panel_separator(self, panel, cx, y, pw):
        pad = 60
        pygame.draw.line(panel, ACCENT_PRIMARY, (pad, y), (pw - pad, y), 1)

    def _game_over_buttons(self, panel, pw, ph, panel_mouse):
        btn_w, btn_h, gap = 210, 46, 26
        total_w = btn_w * 2 + gap
        left = (pw - total_w) // 2
        y = ph - 64
        options = [
            ("Reiniciar [R]", ACCENT_SUCCESS, "restart"),
            ("Menu [Esc]", ACCENT_PRIMARY, "menu"),
        ]
        for i, (label, color, action) in enumerate(options):
            rect = pygame.Rect(left + i * (btn_w + gap), y, btn_w, btn_h)
            hovered = rect.collidepoint(panel_mouse)
            base = tuple(min(255, int(c * 1.25)) for c in BG_SECONDARY)
            pygame.draw.rect(panel, base if hovered else BG_SECONDARY, rect,
                             border_radius=10)
            pygame.draw.rect(panel, color, rect, 3 if hovered else 2,
                             border_radius=10)
            _, text = self._render_fitting_text(label, [22, 20, 18, 16],
                                                btn_w - 16, TEXT_PRIMARY)
            panel.blit(text, text.get_rect(center=rect.center))
            self._game_over_rects_local.append((action, rect.copy()))