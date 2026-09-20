import random
from card import Card

# Los símbolos de las 57 cartas son deterministas (PG(2,7)); se generan y
# verifican una sola vez y luego se reutilizan en cada partida nueva.
_SYMBOLS_CACHE = None


class Deck:
    def __init__(self):
        self.cards = []
        self.generate_dobble_deck()

    def generate_dobble_deck(self):
        """Genera mazo Dobble usando plano proyectivo PG(2,7) (orden 7).
        
        Construcción matemática estándar:
        - q = 7 (primo)
        - Puntos: clases de equivalencia de (x,y,z) ∈ GF(7)³ sin (0,0,0) / ~
        - Rectas: clases de equivalencia de [a,b,c] ∈ GF(7)³ sin (0,0,0) / ~
        - Incidencia: punto (x,y,z) ∈ recta [a,b,c] ⟺ a*x + b*y + c*z ≡ 0 (mod 7)
        
        Normalización: escalamos para que la primera coordenada no-cero sea 1.
        
        Resultado: 57 cartas, 57 símbolos, 8 por carta, 1 en común por par.
        """
        global _SYMBOLS_CACHE

        if _SYMBOLS_CACHE is None:
            q = 7

            def normalize_point(x, y, z):
                """Normaliza punto: primera coordenada no-cero = 1"""
                for v in (x, y, z):
                    if v != 0:
                        inv = pow(v, -1, q)  # inverso multiplicativo en GF(7)
                        return ((x * inv) % q, (y * inv) % q, (z * inv) % q)
                return (0, 0, 0)  # no debería ocurrir

            def normalize_line(a, b, c):
                """Normaliza recta: primera coordenada no-cero = 1"""
                for v in (a, b, c):
                    if v != 0:
                        inv = pow(v, -1, q)
                        return ((a * inv) % q, (b * inv) % q, (c * inv) % q)
                return (0, 0, 0)

            # --- Generar 57 puntos únicos (clases de equivalencia) ---
            points_set = set()
            for x in range(q):
                for y in range(q):
                    for z in range(q):
                        if (x, y, z) != (0, 0, 0):
                            points_set.add(normalize_point(x, y, z))
            points = sorted(points_set)  # orden determinístico

            # --- Generar 57 rectas únicas ---
            lines_set = set()
            for a in range(q):
                for b in range(q):
                    for c in range(q):
                        if (a, b, c) != (0, 0, 0):
                            lines_set.add(normalize_line(a, b, c))
            lines = sorted(lines_set)

            assert len(points) == 57, f"Puntos: {len(points)}"
            assert len(lines) == 57, f"Rectas: {len(lines)}"

            # --- Calcular incidencia: cada recta contiene 8 puntos ---
            cards_symbols = []
            for line in lines:
                a, b, c = line
                card = []
                for idx, (x, y, z) in enumerate(points):
                    if (a * x + b * y + c * z) % q == 0:
                        card.append(idx)
                cards_symbols.append(card)

            # Verificación (una sola vez)
            self._verify_deck(cards_symbols, q)
            _SYMBOLS_CACHE = cards_symbols

        # Crear objetos Card
        self.cards = [Card(i, symbols)
                      for i, symbols in enumerate(_SYMBOLS_CACHE)]

    def _verify_deck(self, cards_symbols, q):
        """Verifica propiedades matemáticas del mazo."""
        total = q * q + q + 1  # 57
        per_card = q + 1        # 8
        
        assert len(cards_symbols) == total, f"Cartas: {len(cards_symbols)} ≠ {total}"
        
        for i, card in enumerate(cards_symbols):
            assert len(card) == per_card, f"Carta {i}: {len(card)} ≠ {per_card}"
            assert len(set(card)) == per_card, f"Carta {i} tiene duplicados"
        
        # Propiedad Dobble: cada par comparte exactamente 1 símbolo
        from itertools import combinations
        for c1, c2 in combinations(cards_symbols, 2):
            common = len(set(c1) & set(c2))
            assert common == 1, f"Par comparte {common} símbolos"

    def shuffle(self):
        random.shuffle(self.cards)

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        return None

    def remaining(self):
        return len(self.cards)