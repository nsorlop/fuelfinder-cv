"""Metricas de precio: marca frente a low-cost."""

from __future__ import annotations

import statistics
from collections import Counter

from fuelfinder.brands import HIPER, LOWCOST, MARCA, OTRAS
from fuelfinder.geo import km
from fuelfinder.normalize import Station


def median_price(stations: list[Station], grupo: str, combustible: str) -> float | None:
    precios = [getattr(s, combustible) for s in stations
               if s.grupo == grupo and getattr(s, combustible) is not None]
    return statistics.median(precios) if precios else None


def nearby_savings(stations: list[Station], combustible: str,
                   radio_km: float) -> tuple[list[float], int, int]:
    """Para cada gasolinera de marca, ahorro frente a la low-cost mas barata cercana.

    Devuelve (ahorros por litro, marcas con alguna low-cost cercana, marcas con precio).
    Solo compara contra LOWCOST: una independiente barata no cuenta.
    """
    lowcost = [s for s in stations if s.grupo == LOWCOST and getattr(s, combustible) is not None]
    marcas = [s for s in stations if s.grupo == MARCA and getattr(s, combustible) is not None]
    ahorros = []
    for m in marcas:
        cercanas = [getattr(l, combustible) for l in lowcost
                    if km((m.lat, m.lon), (l.lat, l.lon)) <= radio_km]
        if cercanas:
            ahorros.append(getattr(m, combustible) - min(cercanas))
    return ahorros, len(ahorros), len(marcas)


def day_summary(stations: list[Station], provincia: str | None,
                radio_km: float = 3, deposito_l: float = 50) -> dict:
    """Resumen de un dia, opcionalmente filtrado por provincia."""
    st = [s for s in stations if provincia is None or s.provincia == provincia]
    n = Counter(s.grupo for s in st)
    marca95, low95 = median_price(st, MARCA, "g95"), median_price(st, LOWCOST, "g95")
    marcad, lowd = median_price(st, MARCA, "diesel"), median_price(st, LOWCOST, "diesel")
    ahorros, con, total = nearby_savings(st, "diesel", radio_km)
    return {
        "n": {g: n.get(g, 0) for g in (MARCA, LOWCOST, HIPER, OTRAS)},
        "median_marca_g95": marca95, "median_lowcost_g95": low95,
        "gap_g95": None if marca95 is None or low95 is None else marca95 - low95,
        "median_marca_diesel": marcad, "median_lowcost_diesel": lowd,
        "gap_diesel": None if marcad is None or lowd is None else marcad - lowd,
        "marcas_con_lowcost": con, "marcas_total": total,
        "pct_marca_con_lowcost": 100 * con / total if total else None,
        "ahorro_deposito_diesel": deposito_l * statistics.median(ahorros) if ahorros else None,
    }
