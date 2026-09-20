import os

import pygame

from constants import SOUNDS_DIR

# Mapa interno -> archivo real en assets/sounds
FILES = {
    "coincidence": "coincidence.mp3",
    "error": "error.mp3",
    "game_over": "gameOver.mp3",
    "start": "startGame2.mp3",
    "lobby": "lobbySound.mp3",
    "lobby_alt": "lobbySound2.mp3",
    "game": "loopSound.mp3",
    "navigate": "efectOver.mp3",
    "select": "select.mp3",
}

# Efectos cortos (se mezclan encima; no interrumpen la musica)
EFFECTS = ("coincidence", "error", "game_over", "start", "navigate", "select")


class SoundManager:
    def __init__(self, effect_volume=0.7, music_volume=0.5):
        self.enabled = False
        self._effects = {}
        self._music = None
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=44100, size=-16,
                                  channels=2, buffer=512)
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
        self._fade_ms = 0
        self._fade_start = 0
        self._fade_vol = music_volume

    def play_effect(self, name, volume=None):
        if not self.enabled:
            return
        sound = self._effects.get(name)
        if not sound:
            return
        if volume is None:
            sound.play()
        else:
            prev = sound.get_volume()
            sound.set_volume(volume)
            sound.play()
            sound.set_volume(prev)

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
            self._fade_ms = 0
        except pygame.error:
            pass

    def fade_in_music(self, track, fade_ms=2000, delay_ms=0, loop=True):
        """Arranca una pista en silencio y sube su volumen gradualmente,
        opcionalmente tras `delay_ms` milisegundos."""
        if not self.enabled:
            return
        path = os.path.join(SOUNDS_DIR, FILES.get(track, ""))
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1 if loop else 0)
            self._music = track
            self._fade_start = pygame.time.get_ticks() + max(0, delay_ms)
            self._fade_ms = max(1, fade_ms)
            self._fade_vol = self.music_volume
        except pygame.error:
            pass

    def fade_out_music(self, ms=400):
        """Baja y detiene la musica actual sin bloquear."""
        if not self.enabled:
            return
        pygame.mixer.music.fadeout(ms)
        self._music = None
        self._fade_ms = 0

    def effect_length(self, name):
        """Duracion en segundos de un efecto (0 si no esta disponible)."""
        sound = self._effects.get(name)
        if not sound:
            return 0.0
        return sound.get_length()

    def update(self):
        """Sube el volumen de la musica de forma gradual (llamar cada frame)."""
        if not self.enabled or not self._music or not self._fade_ms:
            return
        t = (pygame.time.get_ticks() - self._fade_start) / self._fade_ms
        if t < 0:
            pygame.mixer.music.set_volume(0.0)
        elif t >= 1.0:
            self._fade_ms = 0
            pygame.mixer.music.set_volume(self._fade_vol)
        else:
            pygame.mixer.music.set_volume(
                self._fade_vol * max(0.0, min(1.0, t)))

    def stop_music(self):
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        self._music = None