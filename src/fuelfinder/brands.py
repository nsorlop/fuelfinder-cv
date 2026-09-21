"""Clasificacion de gasolineras por su rotulo comercial.

El criterio es conservador a proposito: ante la duda, una gasolinera va a
OTRAS y queda fuera de la comparacion marca/low-cost. Asi ningun error de
clasificacion puede inflar la diferencia de precio que se publica.
"""

from __future__ import annotations

import re
import unicodedata

MARCA = "marca"
LOWCOST = "lowcost"
HIPER = "hiper"
OTRAS = "otras"

# Grandes petroleras integradas. Sin ambiguedad.
_MARCAS = ("REPSOL", "CEPSA", "MOEVE", "BP", "SHELL", "GALP", "PETRONOR")

# Cadenas desatendidas cuyo modelo de negocio es el precio.
# PLENERGY es el nombre actual de PLENOIL: se incluyen ambos.
_LOWCOST = ("PLENERGY", "PLENOIL", "BALLENOIL", "PETROPRIX", "GASEXPRESS",
            "BONAREA", "LOW COST")

# Baratas, pero no low-cost en sentido estricto. Se separan para no mezclar.
_HIPER = ("CARREFOUR", "ALCAMPO")

# Rotulos que encajarian en un grupo por su nombre pero que se excluyen
# deliberadamente. CAMPSA EXPRESS es la marca barata de Repsol: ni marca
# ni low-cost limpiamente.
_EXCLUIDOS = ("CAMPSA EXPRESS",)


def _normaliza(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in sin_acentos if not unicodedata.combining(c)).upper().strip()


def _contiene_palabra(texto: str, termino: str) -> bool:
    # Palabra completa: "BP" no debe coincidir dentro de "BPX".
    return re.search(rf"(?<![A-Z0-9]){re.escape(termino)}(?![A-Z0-9])", texto) is not None


def classify(rotulo: str | None) -> str:
    """Devuelve MARCA, LOWCOST, HIPER u OTRAS para un rotulo comercial."""
    if not rotulo:
        return OTRAS
    texto = _normaliza(rotulo)
    if any(_contiene_palabra(texto, t) for t in _EXCLUIDOS):
        return OTRAS
    if any(_contiene_palabra(texto, t) for t in _LOWCOST):
        return LOWCOST
    if any(_contiene_palabra(texto, t) for t in _HIPER):
        return HIPER
    if any(_contiene_palabra(texto, t) for t in _MARCAS):
        return MARCA
    return OTRAS
