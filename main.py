
import pygame
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game import Game

def main():
    pygame.init()
    juego = Game()
    juego.run()

if __name__ == "__main__":
    main()