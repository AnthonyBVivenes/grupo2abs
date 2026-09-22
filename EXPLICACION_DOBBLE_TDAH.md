# DOBBLE - Guía Completa del Juego (Diseñado para TDAH)

---

## 🎮 **Cómo se Juega**

**Objetivo**: Identificar el **único símbolo común** entre tu carta y la carta central antes que tu oponente (o antes de que se acabe el tiempo).

- **Mazo**: 57 cartas generadas matemáticamente (plano proyectivo PG(2,7)) — **cada par comparte exactamente 1 símbolo**
- **8 símbolos por carta** en layout 3-2-3 centrado
- **Dinámica**:
  1. Se muestra una carta central
  2. Cada jugador tiene su carta
  3. Al encontrar el símbolo coincidente, presionas la tecla correspondiente
  4. ¡Ganas la carta central y se revela la siguiente!
  5. Gana quien consiga más cartas al terminar el mazo o el tiempo

---

## 🎯 **Modos de Juego**

### **1 JUGADOR** (Contra reloj)
- Juegas solo contra el temporizador
- Configurable: **Sin límite / 30s / 60s / 90s**
- Ideal para entrenar **velocidad de procesamiento** y **atención sostenida**
- Puntuación final con estadísticas (aciertos, errores, tiempo)

### **MULTIJUGADOR LOCAL** (2 jugadores, mismo teclado)
- **Jugador 1**: Teclas `Q W E R A S D F` (personalizables)
- **Jugador 2**: Teclas `1 2 3 4 5 6 7 8` (personalizables)
- Turnos simultáneos — quien acierte primero se lleva la carta
- **Pausa disponible** (tecla `ESC`) para regular ritmo

### **MULTIJUGADOR REMOTO** (Red local/Internet)
- Arquitectura **cliente-servidor** (TCP)
- Un jugador **Host** (crea partida), otro **Cliente** (se une por IP)
- Sincronización de estado en tiempo real
- Chat de estado (esperando, conectado, cartas restantes)
- **Sin pausa** (por sincronización de red)

---

## 🎨 **Interfaz Gráfica y Menús**

### **Menú Principal**
```
┌─────────────────────┐
│      DOBBLE         │  ← Título con animación "respiración"
├─────────────────────┤
│  ▸ 1 JUGADOR        │
│    MULTIJUGADOR     │
│    LOCAL            │
│    MULTIJUGADOR     │
│    REMOTO           │
│    CONFIGURACIÓN    │
│    SALIR            │
└─────────────────────┘
```
- Navegación con **flechas ↑↓** + **Enter**
- Fondo difuminado con velo oscuro para foco
- Música de lobby relajante (loop suave)

### **Pantalla de Juego (PLAYING)**
```
┌─────────────────────────────────────┐
│  [Jugador 1]    TIEMPO: 45s    [J2] │  ← Panel superior con scores
│        ┌─────────┐                  │
│        │  CARTA  │                  │  ← Carta central GRANDE
│        │ CENTRAL │                  │
│        └─────────┘                  │
│  ┌─────────┐              ┌─────────┐
│  │ TU CARTA│              │CARTA J2 │  ← Cartas de jugadores (lado)
│  │  (8 sym)│              │ (8 sym) │
│  └─────────┘              └─────────┘
│  Q W E R                    1 2 3 4  ← Guía de teclas (overlay)
│  A S D F                    5 6 7 8
└─────────────────────────────────────┘
```
- **Intro animada**: 3-2-1-GO con cuenta regresiva visual
- **Feedback inmediato**: Partículas doradas + sonido al acertar / vibración + sonido error al fallar
- **Pista visual opcional**: Al fallar, resalta el símbolo correcto brevemente

### **Configuración (SETTINGS)**
Panel scrollable con 10 opciones editables:

| Opción | Tipo | Valores | Beneficio TDAH |
|--------|------|---------|----------------|
| **Duración partida** | Choice | Sin límite / 30s / 60s / 90s | Controla tiempo de atención sostenida |
| **Tamaño cartas** | Choice | Pequeña / Normal / Grande | Reduce carga visual / accesibilidad |
| **Pista al fallar** | Choice | No / Sí | Refuerzo positivo vs frustración |
| **Penalización fallo** | Choice | Ninguna / Leve / Fuerte | Ajusta presión competitiva |
| **Nombre Jugador 1/2** | Texto | Editable | Personalización, identidad |
| **Teclas Jugador 1/2** | 8 teclas | Editor visual | Adaptación motora, comodidad |
| **Pantalla completa** | Choice | Ventana / Pantalla completa | Elimina distracciones de escritorio |
| **Pausa tras acierto** | Choice | 0.15s / 0.30s / 0.50s | Controla ritmo, evita clicks impulsivos |

- **Navegación**: ↑↓ (opciones), ←→ (cambiar valores), Enter (editar texto/teclas)
- **Guardado automático** en `config.json` (persistente entre sesiones)

---

## 🧠 **Diseño Específico para TDAH**

### **Paleta de Colores (Lospec 500 — 42 colores)**
- **Fondo/Primarios**: Tonos fríos apagados (cian suave `#4ecdc4`, verde azulado `#26a69a`)
- **Acento dorado** `#ffd700` **SOLO** para celebraciones (logros, aciertos)
- **Sin elementos parpadeantes** innecesarios
- **Contraste alto** para legibilidad

### **Mecánicas Anti-Sobrecarga**
| Característica | Propósito TDAH |
|----------------|----------------|
| Layout 3-2-3 centrado | Percepción visual organizada, reduce búsqueda caótica |
| Cartas escalables (3 tamaños) | Adapta carga visual a necesidad individual |
| Input lock (0.15–0.50s) | Previene respuestas impulsivas tras acierto |
| Pista visual opcional | Andamiaje: apoyo sin quitar autonomía |
| Pausa en local | Autorregulación: jugador controla ritmo |
| Feedback bimodal (visual+audio) | Refuerzo multisensorial inmediato |
| Nombres/teclas personalizables | Sentido de agencia y control |

### **Funciones Cognitivas Entrenadas**
- **Atención selectiva**: Filtrar 7 distractores para hallar 1 objetivo
- **Atención sostenida**: Mantener foco durante toda la partida
- **Control de impulsos**: Verificar antes de presionar (input lock)
- **Velocidad de procesamiento**: Identificación rápida de patrones
- **Memoria de trabajo**: Comparar símbolos carta-mano vs carta-centro
- **Tolerancia a frustración**: Competencia justa, feedback inmediato, partidas cortas

---

## ⌨️ **Controles Principales**

| Contexto | Teclas |
|----------|--------|
| **Menús** | ↑↓ navegar · Enter seleccionar · ESC volver |
| **Juego (J1)** | 8 teclas personalizables (default: QWER ASDF) |
| **Juego (J2)** | 8 teclas personalizables (default: 1234 5678) |
| **Pausa (local)** | ESC abre menú pausa |
| **Debug layout** | Tecla `D` (editor visual posiciones símbolos) |
| **Configuración** | Enter editar · ←→ cambiar · ESC cancelar/guardar |

---

## 📁 **Estructura del Proyecto**

```
grupo2abs/
├── main.py                 # Punto de entrada (16 líneas)
├── config.json             # Configuración persistente
├── README.md               # Documentación básica
├── INFORME_DOBBLE_TDAH.md  # Informe técnico completo
├── assets/
│   ├── fonts/              # Fuentes pixel-art (04b_30, Minecraft, etc.)
│   ├── sounds/             # Efectos y música (MP3)
│   └── sprites/            # 57 símbolos + base de carta + symbol_map.json
└── src/
    ├── card.py             # Renderizado y lógica de cartas
    ├── deck.py             # Generación matemática del mazo (PG(2,7))
    ├── player.py           # Estado y lógica del jugador
    ├── game.py             # Motor principal, máquina de estados
    ├── sound.py            # Gestión de audio
    ├── config.py           # Persistencia de configuración
    ├── constants.py        # Constantes, colores, rutas, fuentes
    ├── palette.py          # Paleta Lospec 500 (42 colores)
    ├── ui.py               # Utilidades de UI (render, animaciones, modales)
    ├── net.py              # Red (RemoteHost, RemoteClient)
    └── fonts.py            # Carga de fuentes con fallbacks
```

---

## 🚀 **Cómo Ejecutar**

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

**Requisitos**: Python 3.12+, pygame >= 2.0.0

---

## 📚 **Documentación Adicional**

- `README.md` — Descripción básica y requisitos
- `INFORME_DOBBLE_TDAH.md` — Informe técnico completo (arquitectura, POO, algoritmos)
- `config.json` — Configuración persistente editable manualmente

---

*Documento generado para referencia rápida. Última actualización: Septiembre 2026*