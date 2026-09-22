# Informe del Proyecto Dobble para Personas con TDAH

## 1. Descripción General del Proyecto

**Dobble** es una implementación digital del popular juego de cartas de observación rápida, desarrollado en **Python** con la librería **Pygame**. El proyecto está diseñado específicamente considerando las necesidades de personas con **Trastorno por Déficit de Atención e Hiperactividad (TDAH)**.

### 1.1 Características Principales

- **Mazo matemáticamente exacto**: 57 cartas generadas mediante el plano proyectivo PG(2,7), garantizando que **cada par de cartas comparta exactamente 1 símbolo** (propiedad fundamental de Dobble).
- **8 símbolos por carta**: Distribuidos en layout 3-2-3 centrado para mejor percepción visual.
- **Múltiples modos de juego**:
  - **1 Jugador** (contra reloj, con límite de tiempo configurable)
  - **Multijugador Local** (2 jugadores, teclados separados)
  - **Multijugador Remoto** (red local/Internet, arquitectura cliente-servidor)
- **Accesibilidad y configurabilidad**:
  - Tamaño de cartas ajustable (Pequeña / Normal / Grande)
  - Pistas visuales al fallar (opcional)
  - Penalización por error configurable (Ninguna / Leve / Fuerte)
  - Teclas personalizables por jugador (8 teclas cada uno)
  - Nombres de jugadores editables
  - Pantalla completa / Ventana redimensionable
  - Límite de tiempo configurable (Sin límite / 30s / 60s / 90s)

### 1.2 Beneficios para Personas con TDAH

Según la documentación del proyecto (README.md), el juego estimula:

| Función Cognitiva | Beneficio en TDAH |
|-------------------|-------------------|
| **Atención selectiva** | Filtrar estímulos irrelevantes para encontrar el símbolo común |
| **Atención sostenida** | Mantener el foco durante toda la partida |
| **Control de impulsos** | Evitar responder precipitadamente; requiere verificación visual |
| **Velocidad de procesamiento** | Identificación rápida de patrones visuales entre 8 símbolos |
| **Tolerancia a la frustración** | Entorno social competitivo pero controlado, con feedback inmediato |
| **Memoria de trabajo** | Recordar símbolos vistos y comparar con carta central |

**Diseño amigable para TDAH**:
- Paleta de colores **Lospec 500** con tonos fríos y apagados (cian suave, verde azulado) que reducen la sobrecarga sensorial
- Acento dorado reservado solo para celebraciones (logros), no para elementos distractores
- Interfaz limpia sin elementos parpadeantes innecesarios
- Feedback auditivo y visual inmediato (sonidos de acierto/error, partículas)
- Pausa disponible en modos locales (no en remoto por sincronización)

---

## 2. Arquitectura del Proyecto

### 2.1 Estructura de Archivos

```
grupo2abs/
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias (pygame>=2.0.0)
├── config.json            # Configuración persistente
├── README.md              # Documentación
├── assets/
│   ├── fonts/             # Fuentes pixel-art (04b_30, Minecraft, etc.)
│   ├── sounds/            # Efectos y música (MP3)
│   └── sprites/           # 57 símbolos + base de carta + symbol_map.json
└── src/
    ├── __init__.py
    ├── card.py            # Clase Card - Renderizado y lógica de cartas
    ├── deck.py            # Clase Deck - Generación matemática del mazo (PG(2,7))
    ├── player.py          # Clase Player - Estado y lógica del jugador
    ├── game.py            # Clase Game - Motor principal, máquina de estados
    ├── sound.py           # Clase SoundManager - Gestión de audio
    ├── config.py          # Clase Config - Persistencia de configuración
    ├── constants.py       # Constantes, colores, rutas, fuentes
    ├── palette.py         # Paleta Lospec 500 (42 colores)
    ├── ui.py              # Utilidades de UI (render, animaciones, modales)
    ├── net.py             # Red (RemoteHost, RemoteClient para multijugador)
    └── fonts.py           # Carga de fuentes con fallbacks
```

### 2.2 Diagrama de Clases Simplificado

```
┌─────────────────┐
│      Game       │ ◄──── Controlador principal, máquina de estados
└────────┬────────┘
         │ usa
    ┌────┴────┬──────────────┬─────────────┐
    ▼         ▼              ▼             ▼
┌───────┐ ┌───────┐    ┌──────────┐ ┌────────────┐
│ Deck  │ │Player │    │Card      │ │SoundManager│
└───┬───┘ └───┬───┘    └────┬─────┘ └────────────┘
    │       │             │
    │       │         ┌───┴───┐
    │       │         ▼       ▼
    │       │    ┌─────────┐  (sprites, layout, keys)
    │       │    │  Card   │
    │       │    └─────────┘
    │       ▼
    │  ┌─────────┐
    └─►│  Card   │ (cartas en mano)
       └─────────┘
```

---

## 3. Aplicación de los 4 Pilares de la POO

### 3.1 Encapsulamiento (Encapsulation)

**Definición**: Ocultar los detalles internos de implementación y exponer solo una interfaz pública controlada.

#### En la clase `Card` (`src/card.py`):

```python
class Card:
    # Atributos de CLASE (compartidos) - PRIVADOS por convención (_)
    _sprite_cache = {}      # Caché de sprites cargados
    _card_base = None       # Imagen base de la carta
    _symbol_map = None      # Mapeo ID -> archivo PNG
    _layout_params = {...}  # Parámetros de layout mutables
    _card_w = CARD_WIDTH    # Tamaño de render
    _card_h = CARD_HEIGHT
```

**Mecanismos de encapsulamiento aplicados**:

| Mecanismo | Ejemplo en Card | Propósito |
|-----------|-----------------|-----------|
| **Atributos privados (`_`)** | `_symbol_positions`, `_key_labels`, `_sprite_cache` | Evitar acceso directo externo |
| **Métodos de clase (`@classmethod`)** | `set_card_size()`, `set_layout()`, `get_sprite()`, `card_w()` | Interfaz controlada para estado compartido |
| **Propiedades computadas** | `symbol_size()` retorna `_layout_params['symbol_size']` | Validación/transformación al acceder |
| **Métodos privados (`_`)** | `_calculate_positions()`, `_draw_key_label()`, `_draw_debug()` | Lógica interna no expuesta |
| **Lazy loading** | `get_card_base()`, `get_sprite()`, `_load_symbol_map()` | Carga bajo demanda, caché automático |

#### En la clase `Deck` (`src/deck.py`):

```python
class Deck:
    def __init__(self):
        self.cards = []           # Lista privada de cartas
        self.generate_dobble_deck()  # Generación encapsulada
    
    def shuffle(self):            # Interfaz pública
        random.shuffle(self.cards)
    
    def draw_card(self):          # Interfaz pública controlada
        if self.cards:
            return self.cards.pop()
        return None
    
    def remaining(self):          # Información de estado
        return len(self.cards)
```

- **Caché a nivel de módulo**: `_SYMBOLS_CACHE = None` evita regenerar el mazo matemáticamente costoso en cada partida.

#### En la clase `SoundManager` (`src/sound.py`):

```python
class SoundManager:
    def __init__(self, effect_volume=0.7, music_volume=0.5):
        self.enabled = False
        self._effects = {}        # Diccionario PRIVADO de sonidos cargados
        self._music = None        # Track actual PRIVADO
        self._fade_ms = 0         # Estado de fade PRIVADO
        # ...
    
    def play_effect(self, name, volume=None):  # Interfaz pública
    def play_music(self, track, loop=True):    # Interfaz pública
    def fade_in_music(self, track, fade_ms=2000, delay_ms=0, loop=True):
    def update(self):  # Llamado cada frame para fades
```

#### En la clase `Config` (`src/config.py`):

```python
class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)  # Estado interno encapsulado
        self.load()
    
    def __getitem__(self, key):  # Acceso controlado tipo dict
        return self.data[key]
    
    def __setitem__(self, key, value):  # Validación al escribir
        if key in ("p1_keys", "p2_keys"):
            value = [normalize_key(v) for v in value]
        self.data[key] = value
    
    def save(self):  # Persistencia encapsulada
    def load(self):
```

---

### 3.2 Herencia (Inheritance)

**Definición**: Crear nuevas clases basadas en clases existentes, reutilizando y extendiendo su comportamiento.

#### Análisis en el Proyecto

**Este proyecto usa herencia de forma LIMITADA y deliberada**. En Python, todas las clases heredan implícitamente de `object`, pero no hay una jerarquía de herencia explícita profunda entre las clases del dominio (Card, Deck, Player, Game, etc.).

**Razones de diseño**:
1. **Composición sobre herencia**: El proyecto prefiere **composición** (Game *tiene* Deck, Player, SoundManager, Config) en lugar de herencia.
2. **Clases con responsabilidades únicas (SRP)**: Cada clase tiene un propósito claro y no necesita especializarse.
3. **Simplicidad y mantenibilidad**: Evita jerarquías complejas difíciles de depurar.

#### Donde SÍ aparece herencia (implícita/sutil):

```python
# En card.py - Card no hereda de otra clase del proyecto, pero:
# - Usa duck typing con pygame.Surface
# - Podría considerarse herencia de "objeto renderizable" conceptualmente

# En net.py - RemoteHost y RemoteClient podrían compartir base:
class RemoteHost:
    def __init__(self, port):
        # ... implementación servidor

class RemoteClient:
    def __init__(self, host, port):
        # ... implementación cliente
# Ambos implementan interfaz común: send(), poll(), close(), connected()
# → Polimorfismo de interfaz (ver sección 3.3)
```

#### Patrón Strategy (Alternativa a herencia) en `Game`:

La máquina de estados en `Game` usa **composición de comportamientos** en lugar de subclases:

```python
class Game:
    def __init__(self):
        self.state = "MENU"  # Estado actual
        # Diccionarios de callbacks (Strategy pattern)
        self.menu_options = [
            ("1 JUGADOR", self._new_game),
            ("MULTIJUGADOR LOCAL", self._new_local_game),
            # ...
        ]
        self.pause_options = [
            ("Reanudar", self._resume_game),
            ("Reiniciar", self._pause_restart),
            # ...
        ]
```

Cada opción de menú/pausa es una **estrategia** (callable) distinta, no una subclase.

---

### 3.3 Polimorfismo (Polymorphism)

**Definición**: Capacidad de tratar objetos de diferentes clases de manera uniforme a través de una interfaz común.

#### 3.3.1 Polimorfismo de Interfaz (Duck Typing)

En `net.py`, `RemoteHost` y `RemoteClient` implementan la **misma interfaz** sin herencia común:

```python
# Ambos tienen estos métodos (interfaz implícita):
# - send(msg)
# - poll() -> list[msg]
# - close()
# - connected() -> bool
# - error (atributo)

# En Game._poll_remote():
if self.remote.connected():
    msgs = self.remote.poll()  # Funciona tanto para Host como Client
    self._handle_remote_msgs(msgs)
```

#### 3.3.2 Polimorfismo en `Player` (Comportamiento condicional)

```python
class Player:
    def __init__(self, name, is_human=True):
        self.is_human = is_human  # Bandera que cambia comportamiento
    
    def play_turn(self, game):
        if not self.is_human:     # Polimorfismo por bandera
            # Lógica IA automática
            if game.center_card and self.hand:
                own_card = self.hand[0]
                common = self.find_common_symbol(own_card, game.center_card)
                # ...
        return False
```

#### 3.3.3 Polimorfismo en Máquina de Estados (`Game`)

El método `handle_key()` despacha a diferentes handlers según el estado:

```python
def handle_key(self, key):
    if self.confirm is not None:
        self._handle_confirm_key(key)
        return
    if self.paused:
        self._handle_pause_key(key)
        return
    if self.resuming:
        return
    if self.state == "SETTINGS":
        self._handle_settings_key(key)
        return
    if self.state == "REMOTE":
        self._handle_remote_key(key)
        return
    if self.state == "MENU":
        # ... navegación menú principal
    elif key == pygame.K_ESCAPE and self.state == "PLAYING":
        # ... pausa
```

Mismo método `handle_key()`, **comportamiento diferente** según contexto (estado).

#### 3.3.4 Polimorfismo en Renderizado (`Card.draw()`)

```python
def draw(self, surface, x, y, debug=False):
    # ...
    sprite = self.get_sprite(sym)
    if sprite:
        # Render con sprite real (imagen PNG)
        scaled_sprite = pygame.transform.scale(sprite, (symbol_size, symbol_size))
        surface.blit(scaled_sprite, sprite_rect)
    else:
        # Render fallback: círculo de color (polimorfismo visual)
        color = fallback_colors[sym % len(fallback_colors)]
        pygame.draw.circle(surface, color, (cx, cy), symbol_size // 2)
```

Misma interfaz `draw()`, **implementación diferente** según disponibilidad de assets.

#### 3.3.5 Polimorfismo en `SoundManager` (Efectos vs Música)

```python
def play_effect(self, name, volume=None):
    sound = self._effects.get(name)
    if sound:
        sound.play()  # Canal separado, se mezcla

def play_music(self, track, loop=True):
    pygame.mixer.music.load(path)  # Canal de música (uno solo)
    pygame.mixer.music.play(-1 if loop else 0)
```

Misma clase, **APIs diferentes** para tipos de audio distintos (efectos cortos vs música continua).

---

### 3.4 Abstracción (Abstraction)

**Definición**: Exponer solo las características esenciales de un objeto, ocultando la complejidad subyacente.

#### 3.4.1 `Card` - Abstracción de Renderizado Complejo

```python
# INTERFAZ PÚBLICA SIMPLE:
card = Card(card_id, symbols_list)
card.draw(surface, x, y)           # Dibuja todo: base, borde, 8 símbolos, keys
card.get_symbol_at_pos(mouse_x, mouse_y)  # Detección click
card.get_symbol_by_key(key)        # Input por teclado
card.set_key_labels(labels)        # Configuración teclas
card.to_surface()                  # Surface independiente para escalar/rotar

# COMPLEJIDAD OCULTA:
# - Layout 3-2-3 centrado con espaciado dinámico
# - Carga lazy de sprites HD + escalado en tiempo real
# - Fallback a círculos de color (16 colores Lospec)
# - Caché de sprites a nivel de clase
# - Overlay debug con grid, IDs, cruces, info layout
# - Etiquetas de teclas con fondo semitransparente
```

#### 3.4.2 `Deck` - Abstracción Matemática (PG(2,7))

```python
# INTERFAZ PÚBLICA SIMPLE:
deck = Deck()
deck.shuffle()
card = deck.draw_card()
remaining = deck.remaining()

# COMPLEJIDAD OCULTA (100+ líneas en generate_dobble_deck):
# - Geometría finita: GF(7)³, 57 puntos, 57 rectas
# - Normalización de coordenadas proyectivas
# - Verificación matemática exhaustiva:
#   * 57 cartas, 8 símbolos cada una
#   * Cada par comparte EXACTAMENTE 1 símbolo
# - Caché global _SYMBOLS_CACHE (se genera UNA sola vez)
```

#### 3.4.3 `Game` - Abstracción del Motor de Juego Completo

```python
# INTERFAZ PÚBLICA MÍNIMA:
game = Game()
game.run()  # Bucle principal: handle_events → update → render @ 60 FPS

# COMPLEJIDAD OCULTA (800+ líneas):
# - Máquina de estados: MENU, SETTINGS, REMOTE, PLAYING
# - Intro animada (3-2-1-GO con cuenta regresiva)
# - Gestión de 2 jugadores (local) o remoto (red)
# - Sincronización estado remoto (host/cliente)
# - Temporizador, pausas, confirmaciones modales
# - Editor visual de layout de cartas (tecla D)
# - Configuración persistente (JSON)
# - Feedback visual (partículas) y auditivo
# - Escalado dinámico de UI al redimensionar ventana
```

#### 3.4.4 `SoundManager` - Abstracción de Audio

```python
# INTERFAZ PÚBLICA:
sound = SoundManager(effect_volume=0.7, music_volume=0.5)
sound.play_effect("coincidence")
sound.play_music("game")
sound.fade_in_music("game", fade_ms=2000, delay_ms=500)
sound.fade_out_music(400)
sound.pause_music() / sound.resume_music()
sound.update()  # Llamar cada frame para fades

# COMPLEJIDAD OCULTA:
# - Inicialización mixer con parámetros específicos (44100Hz, 512 buffer)
# - Caché de efectos (Sound objects) + streaming de música
# - Crossfade suave entre tracks (lobby → game)
# - Volumen independiente efectos/música
# - Manejo graceful de errores (archivos faltantes, mixer no disponible)
```

#### 3.4.5 `Config` - Abstracción de Persistencia

```python
# INTERFAZ PÚBLICA (dict-like):
config = Config()
config["time_limit"] = 60
config["card_scale"] = "large"
config.save()  # Persiste a config.json automáticamente

# COMPLEJIDAD OCULTA:
# - Normalización de teclas (limpia '[1]' → '1', mayúsculas)
# - Validación de claves conocidas (ignora claves extra en JSON)
# - Valores por defecto seguros (DEFAULT_CONFIG)
# - Manejo silencioso de errores IO (try/except)
```

---

## 4. Resumen: Cómo los Pilares Mejoran el Proyecto

| Pilar | Aplicación Principal | Beneficio en Este Proyecto |
|-------|---------------------|---------------------------|
| **Encapsulamiento** | Cachés de clase (`Card._sprite_cache`), estado interno (`SoundManager._effects`), validación (`Config.__setitem__`) | **Mantenibilidad**: Cambios internos no rompen código externo. **Rendimiento**: Cachés transparentes. **Robustez**: Validación automática. |
| **Herencia** | Uso mínimo deliberado; composición preferida | **Simplicidad**: Sin jerarquías frágiles. **Flexibilidad**: Fácil añadir modos sin refactorizar clases base. |
| **Polimorfismo** | Interfaz común `RemoteHost/RemoteClient`, máquina de estados, fallback visual, IA vs humano | **Extensibilidad**: Nuevo modo de red = nueva clase con misma interfaz. **Limpieza**: Un `handle_key` despacha a lógica específica. |
| **Abstracción** | `Deck` (matemáticas), `Card` (render), `Game` (motor), `SoundManager` (audio), `Config` (persistencia) | **Usabilidad**: API simple para lógica compleja. **Separación de concerns**: Cada clase resuelve UN problema bien. **Testabilidad**: Fácil mockear interfaces. |

---

## 5. Conclusiones

El proyecto **Dobble** demuestra una aplicación **pragmática y efectiva** de los principios de POO:

1. **Encapsulamiento** es el pilar más utilizado (cachés, lazy loading, validación, estado privado)
2. **Abstracción** permite que `main.py` tenga solo 16 líneas: `Game().run()`
3. **Polimorfismo** se logra mediante **duck typing** y **máquina de estados**, no herencia forzada
4. **Herencia** se evita intencionalmente a favor de **composición**, resultando en código más modular y testeable

El diseño resultante es **robusto, extensible y accesible**, cumpliendo el objetivo de ser una herramienta terapéutica lúdica para personas con TDAH.