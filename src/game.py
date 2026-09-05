import pygame
import sys
from constants import *
from deck import Deck
from player import Player

class Game:
    def __init__(self, num_humans=1, num_ais=1):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dobble")
        self.clock = pygame.time.Clock()
        self.running = True

        self.deck = Deck()
        self.deck.shuffle()

        self.players = []
        for i in range(num_humans):
            self.players.append(Player(f"Human {i+1}", is_human=True))
        for i in range(num_ais):
            self.players.append(Player(f"AI {i+1}", is_human=False))

        for player in self.players:
            card = self.deck.draw_card()
            if card:
                player.add_card(card)

        self.current_player_index = 0

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

    def update(self):
        current_player = self.players[self.current_player_index]
        if not current_player.is_human:
            if self.deck.remaining() > 0:
                if current_player.play_turn(self):
                    self.next_turn()
        if self.deck.remaining() == 0:
            self.end_game()

    def render(self):
        self.screen.fill(GRAY)
        font = pygame.font.Font(None, 36)
        text = font.render("Dobble - Plantilla", True, BLACK)
        self.screen.blit(text, (50, 50))
        remaining_text = font.render(f"Cartas en mazo: {self.deck.remaining()}", True, BLACK)
        self.screen.blit(remaining_text, (50, 100))
        pygame.display.flip()

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def end_game(self):
        winner = max(self.players, key=lambda p: p.score)
        print(f"Ganador: {winner.name} con {winner.score} cartas")
        self.running = False