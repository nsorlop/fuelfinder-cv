"""Distancias sobre la superficie terrestre."""

from __future__ import annotations

import math

RADIO_TIERRA_KM = 6371.0


def km(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia en linea recta (haversine) entre dos puntos (lat, lon).

    Es distancia en linea recta, NO por carretera. Se declara asi en la web.
    """
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * RADIO_TIERRA_KM * math.asin(math.sqrt(h))
