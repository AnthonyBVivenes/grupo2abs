import os

import pygame

from constants import SOUNDS_DIR

# Mapa interno -> archivo real en assets/sounds
FILES = {
    "coincidence": "coincidence.mp3",
    "error": "error.mp3",
    "game_over": "gameOver.mp3",
    "start": "starGame.mp3",
    "lobby": "lobbySound.mp3",
    "lobby_alt": "lobbySound2.mp3",
    "game": "loopSound.mp3",
}

# Efectos cortos (se mezclan encima; no interrumpen la musica)
EFFECTS = ("coincidence", "error", "game_over", "start")


class SoundManager:
    def __init__(self, effect_volume=0.7, music_volume=0.5):
        self.enabled = False
        self._effects = {}
        self._music = None
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16,
                                  channels=8, buffer=512)
        except pygame.error:
            return
        self.enabled = True
        for name in EFFECTS:
            path = os.path.join(SOUNDS_DIR, FILES[name])
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(effect_volume)
                    self._effects[name] = sound
                except pygame.error:
                    pass
        self.music_volume = music_volume

    def play_effect(self, name):
        if not self.enabled:
            return
        sound = self._effects.get(name)
        if sound:
            sound.play()

    def play_music(self, track, loop=True):
        if not self.enabled:
            return
        if self._music == track and pygame.mixer.music.get_busy():
            return
        path = os.path.join(SOUNDS_DIR, FILES.get(track, ""))
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self._music = track
        except pygame.error:
            pass

    def stop_music(self):
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        self._music = None