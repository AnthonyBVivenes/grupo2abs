import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, '..', 'config.json')

DEFAULT_CONFIG = {
    "time_limit": 60,
    "card_scale": "normal",
    "hint_on_error": True,
    "miss_penalty": "light",
    "player_names": ["Jugador 1", "Jugador 2"],
    "fullscreen": False,
    "input_lock_ms": 300,
}


class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            for key in DEFAULT_CONFIG:
                if key in loaded:
                    self.data[key] = loaded[key]
        except (OSError, ValueError):
            pass

    def save(self):
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value