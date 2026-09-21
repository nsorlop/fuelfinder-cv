"""Conversion de los registros del Ministerio a objetos manejables."""

from __future__ import annotations

from dataclasses import dataclass

from fuelfinder.brands import classify


@dataclass(frozen=True)
class Station:
    id: str
    rotulo: str
    grupo: str
    municipio: str
    provincia: str
    direccion: str
    horario: str
    lat: float
    lon: float
    g95: float | None
    diesel: float | None


def parse_price(texto: str | None) -> float | None:
    """'1,979' -> 1.979. El Ministerio usa coma decimal; vacio significa sin precio."""
    if texto is None:
        return None
    limpio = texto.strip().replace(",", ".")
    return float(limpio) if limpio else None


def parse_station(raw: dict) -> Station | None:
    """Convierte un registro crudo. Sin coordenadas no sirve para el mapa: None."""
    lat = parse_price(raw.get("Latitud"))
    lon = parse_price(raw.get("Longitud (WGS84)"))
    if lat is None or lon is None:
        return None
    rotulo = (raw.get("Rótulo") or "").strip()
    return Station(
        id=str(raw.get("IDEESS", "")),
        rotulo=rotulo,
        grupo=classify(rotulo),
        municipio=(raw.get("Municipio") or "").strip(),
        provincia=(raw.get("Provincia") or "").strip(),
        direccion=(raw.get("Dirección") or "").strip(),
        horario=(raw.get("Horario") or "").strip(),
        lat=lat,
        lon=lon,
        g95=parse_price(raw.get("Precio Gasolina 95 E5")),
        diesel=parse_price(raw.get("Precio Gasoleo A")),
    )
