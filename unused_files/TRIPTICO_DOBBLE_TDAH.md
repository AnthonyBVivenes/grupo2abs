# DOBBLE — Tríptico Informativo

---

## 📖 **DESCRIPCIÓN BREVE**

**Dobble** es la adaptación digital del clásico juego de observación rápida, desarrollado en **Python + Pygame** y diseñado específicamente para **personas con TDAH**.

- **57 cartas únicas**, **8 símbolos cada una**, generadas con **geometría finita (PG(2,7))** — garantía matemática de que *todo par comparte exactamente 1 símbolo*
- **3 modos**: 1 jugador (contrarreloj), 2 jugadores local (mismo teclado), 2 jugadores remoto (red/Internet)
- **Interfaz accesible**: paleta Lospec 500 (tonos fríos, sin parpadeos), cartas redimensionables, teclas y nombres personalizables, pistas opcionales, pausa en local
- **Objetivo terapéutico**: entrena **atención selectiva/sostenida, control de impulsos, velocidad de procesamiento, memoria de trabajo y tolerancia a la frustración** mediante partidas cortas, feedback inmediato y ritmo configurable

---

## 🎮 **CÓMO SE JUEGA**

**Objetivo**: Encuentra el **único símbolo común** entre tu carta y la carta central antes que tu rival (o antes de que acabe el tiempo).

**Mazo**: 57 cartas (PG(2,7)), 8 símbolos/carta en layout 3-2-3 centrado. *Propiedad clave: cualquier par comparte exactamente 1 símbolo*.

**Dinámica**: 1) Carta central visible → 2) Cada jugador tiene su carta → 3) Detectas coincidencia → pulsas tu tecla → 4) Ganas la carta central → 5) Gana quien más cartas acumule.

### 3 MODOS

| Modo | Jugadores | Controles | Clave |
|------|-----------|-----------|-------|
| **1 JUGADOR** | 1 vs reloj | 8 teclas configurables | Velocidad y atención sostenida |
| **LOCAL** | 2 (1 teclado) | J1: QWER/ASDF · J2: 1234/5678 | Pausa disponible (ESC) |
| **REMOTO** | 2 (red/Internet) | Cada uno en su PC | Cliente-servidor TCP, sin pausa |

⚙️ **Tiempo**: Sin límite / 30s / 60s / 90s  •  🔧 **Todo personalizable**: nombres, teclas, tamaño cartas, penalizaciones

---

## 🧠 **BENEFICIOS PARA TDAH**

### Paleta Sensorial (Lospec 500)
Fondo en tonos fríos apagados (cian `#4ecdc4`, verde azulado `#26a69a`). **Acento dorado `#ffd700` solo para logros**. Sin parpadeos, alto contraste, fuentes pixel-art legibles.

### Mecánicas Anti-Sobrecarga
El **layout 3-2-3 centrado** guía la mirada y reduce búsqueda caótica. **3 tamaños de carta** adaptan carga visual. **Input lock (0.15–0.50 s)** frena impulsividad tras acierto. **Pista visual opcional** resalta el símbolo correcto al fallar (andamiaje sin quitar autonomía). **Pausa en local (ESC)** para autorregular ritmo. **Feedback bimodal inmediato** (partículas + sonido acierto / vibración + sonido error) refuerza por vía visual y auditiva. **Teclas y nombres editables** dan agencia y control.

### Funciones Cognitivas Entrenadas
**Atención selectiva**: filtrar 7 distractores → hallar 1 objetivo. **Atención sostenida**: foco continuo toda la partida. **Control de impulsos**: input lock obliga a verificar antes de pulsar. **Velocidad de procesamiento**: identificar patrones visuales en fracciones de segundo. **Memoria de trabajo**: comparar carta propia vs. carta central. **Tolerancia a frustración**: partidas cortas, feedback justo, reintento inmediato.

---

## 🏗️ **4 PILARES POO EN EL PROYECTO**

### 🔒 Encapsulamiento
**Aplicación**: Cachés de clase (`Card._sprite_cache`), estado privado (`SoundManager._effects`), validación al escribir (`Config.__setitem__`), caché de módulo (`Deck._SYMBOLS_CACHE`).
**Archivos**: `card.py`, `sound.py`, `config.py`, `deck.py`
**Ganancia**: Mantenibilidad, rendimiento, robustez.

### 🧩 Herencia (mínima, composición > herencia)
**Aplicación**: `Game` *tiene* Deck/Player/Sound/Config (no hereda). SRP en cada clase. Strategy en menús (callbacks, no subclases). `RemoteHost/Client` comparten interfaz sin herencia común.
**Archivos**: `game.py`, `net.py`
**Ganancia**: Simplicidad, flexibilidad, sin jerarquías frágiles.

### 🔄 Polimorfismo
**Aplicación**: Duck typing red (`send/poll/connected`), máquina de estados (`handle_key` despacha según estado), fallback visual (`Card.draw`: PNG o círculos), IA vs humano (`Player.is_human`), efectos vs música (canales múltiples vs streaming).
**Archivos**: `game.py`, `card.py`, `player.py`, `sound.py`, `net.py`
**Ganancia**: Extensibilidad, código limpio, un método = múltiples comportamientos.

### 📦 Abstracción
**Aplicación**: `Card.draw()` oculta layout 3-2-3, caché, fallback, debug. `Deck()` oculta geometría finita GF(7)³ + verificación 57×8. `Game.run()` oculta bucle 60 FPS, estados, sync red, partículas, config. `SoundManager` oculta mixer, crossfade, volúmenes. `Config` oculta JSON, normalización, defaults.
**Archivos**: `card.py`, `deck.py`, `game.py`, `sound.py`, `config.py`
**Ganancia**: `main.py` = 16 líneas (`Game().run()`), separación de concerns, testeable.

---

## 📦 **RESUMEN TÉCNICO**

- **Stack**: Python 3.12+ · Pygame 2.0+ · TCP sockets · JSON config
- **Equipo**: Anthony Vivenes · Abelardo Drika · Pedro Alejandro · Alexander López
- **Ejecutar**: `pip install -r requirements.txt && python main.py`

---

*Dobble — Juego terapéutico lúdico para atención, impulso y velocidad de procesamiento*