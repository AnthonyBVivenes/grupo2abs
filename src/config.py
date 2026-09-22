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
    "p1_keys": ["Q", "W", "E", "R", "A", "S", "D", "F"],
    "p2_keys": ["1", "2", "3", "4", "5", "6", "7", "8"],
    "remote_ip": "127.0.0.1",
    "remote_port": 7777,
    "music_volume": 0.5,
    "effect_volume": 0.7,
    "music_muted": False,
    "effects_muted": False,
}


def _clean_key(value):
    """Limpia el nombre de una tecla: quita corchetes raros (p.ej. '[1]' -> '1')."""
    if not isinstance(value, str):
        return value
    value = value.strip()
    if len(value) >= 2 and value.startswith("[") and value.endswith("]") \
            and value[1:-1].strip().isalnum():
        value = value[1:-1].strip()
    return value.upper()


def normalize_key(value):
    """Tecla normalizada tal y como se guarda/usa en el juego."""
    cleaned = _clean_key(value)
    return cleaned.upper() if cleaned else cleaned


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
                    if key in ("p1_keys", "p2_keys"):
                        self.data[key] = [normalize_key(v) for v in loaded[key]]
                    else:
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
        if key in ("p1_keys", "p2_keys"):
            value = [normalize_key(v) for v in value]
        self.data[key] = value