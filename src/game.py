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
        self._restart()

    def _restart(self):
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
        self.center_card_pos = (0, 0)
        self.player_card_pos = (0, 0)

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
                if event.key == pygame.K_r and self.game_over:
                    self._restart()

    def update(self):
        pass

    def handle_click(self, pos):
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
                sym, _ = hit
                if sym in self.center_card.symbols:
                    self._on_correct(player, card)
                else:
                    self._on_incorrect(player)

    def _on_correct(self, player, card):
        player.score += 1
        player.correct += 1
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

    def _on_incorrect(self, player):
        player.incorrect += 1
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
        screen.fill(BG_COLOR)
        self._draw_stats_panel(screen)
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
        self._draw_message(screen)
        if self.game_over:
            self._draw_game_over(screen)
        pygame.display.flip()

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

    def _draw_message(self, screen):
        if self.message and pygame.time.get_ticks() < self.message_end:
            font = load_font(FONT_SIZE_MESSAGE)
            max_width = self.w - SCORE_PANEL_WIDTH - 40
            my = max(40, self.h // 2 - 130)
            self._render_wrapped_message(screen, self.message, my, max_width, font, self.message_color)

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
            "Pulsa R para reiniciar",
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

    def _render_wrapped_message(self, surface, text, y, max_width, font, color):
        words = text.split()
        lines = []
        current = ""
        for word in words:
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
        center_x = SCORE_PANEL_WIDTH + (self.w - SCORE_PANEL_WIDTH) // 2
        start_y = y - (line_h * (len(lines) - 1)) // 2
        for i, line in enumerate(lines):
            rendered = font.render(line, True, color)
            rect = rendered.get_rect(center=(center_x, start_y + i * line_h))
            surface.blit(rendered, rect)