"""Genera los datos de la web y las imagenes para LinkedIn.

Uso:  python -m fuelfinder.build              (semana anterior a hoy + mapa + imagenes)
      python -m fuelfinder.build 2026-09-21   (semana anterior a esa fecha)
      python -m fuelfinder.build --map-only   (SOLO precios actuales del mapa)

--map-only es lo que ejecuta la actualizacion automatica. No toca el analisis
semanal ni las imagenes: esas cifras son las del post y el carrusel, y la web
tiene que seguir coincidiendo con ellas.
"""

from __future__ import annotations

import datetime
import json
import statistics
import sys
import time
from pathlib import Path

from fuelfinder.analyze import day_summary
from fuelfinder.fetch import current_url, get_json, history_url
from fuelfinder.normalize import Station, parse_station

RAIZ = Path(__file__).resolve().parents[2]
RAW = RAIZ / "data" / "raw"
WEB = RAIZ / "docs"

PROVINCIAS = [
    ("VALENCIA / VALÈNCIA", "Valencia"),
    ("ALICANTE", "Alicante"),
    ("CASTELLÓN / CASTELLÓ", "Castellón"),
    (None, "Comunitat Valenciana"),
]
DIAS = 7
RADIO_KM = 3
DEPOSITO_L = 50


def _stations(datos: dict) -> list[Station]:
    return [s for s in (parse_station(r) for r in datos["ListaEESSPrecio"]) if s]


def _descarga(url: str, destino: Path) -> dict:
    """Descarga y guarda el crudo. Si ya existe, lo reutiliza (no machaca al servidor)."""
    if destino.exists():
        return json.loads(destino.read_text(encoding="utf-8"))
    datos = get_json(url)
    destino.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    time.sleep(1)
    return datos


def _resumen_semana(dias: list[dict]) -> dict:
    def media(clave):
        v = [d[clave] for d in dias if d[clave] is not None]
        return statistics.mean(v) if v else None

    def rango(clave):
        v = [d[clave] for d in dias if d[clave] is not None]
        return [min(v), max(v)] if v else None

    ultimo = dias[-1]
    return {
        "n": ultimo["n"],
        "marcas_total": ultimo["marcas_total"],
        "gap_g95": media("gap_g95"), "gap_g95_rango": rango("gap_g95"),
        "gap_diesel": media("gap_diesel"), "gap_diesel_rango": rango("gap_diesel"),
        "median_marca_g95": media("median_marca_g95"),
        "median_lowcost_g95": media("median_lowcost_g95"),
        "median_marca_diesel": media("median_marca_diesel"),
        "median_lowcost_diesel": media("median_lowcost_diesel"),
        "pct_marca_con_lowcost": media("pct_marca_con_lowcost"),
        "ahorro_deposito_diesel": media("ahorro_deposito_diesel"),
    }


def merge_map_refresh(resumen: dict, precios_mapa: str | None, n_estaciones: int,
                      ahora: str) -> dict:
    """Devuelve una copia del resumen con solo los campos del mapa actualizados."""
    nuevo = dict(resumen)
    nuevo["precios_mapa"] = precios_mapa
    nuevo["n_estaciones"] = n_estaciones
    nuevo["mapa_actualizado"] = ahora
    return nuevo


def _escribir_mapa(mapa: list[Station]) -> None:
    # Formato compacto: una fila por gasolinera, para que la web cargue rapido.
    filas = [[s.lat, s.lon, s.rotulo, s.grupo, s.municipio, s.direccion, s.horario,
              s.g95, s.diesel] for s in mapa]
    (WEB / "data" / "stations.json").write_text(
        json.dumps(filas, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def refresh_map() -> dict:
    """Refresca solo los precios actuales del mapa, conservando el analisis semanal."""
    ruta = WEB / "data" / "summary.json"
    resumen = json.loads(ruta.read_text(encoding="utf-8"))
    actual = get_json(current_url())
    mapa = _stations(actual)
    if not mapa:
        raise RuntimeError("La API no ha devuelto ninguna gasolinera: no se sobrescribe el mapa.")
    resumen = merge_map_refresh(resumen, actual.get("Fecha"), len(mapa),
                                datetime.datetime.now().isoformat(timespec="minutes"))
    ruta.write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    _escribir_mapa(mapa)
    return resumen


def build(hoy: datetime.date) -> dict:
    RAW.mkdir(parents=True, exist_ok=True)
    (WEB / "data").mkdir(parents=True, exist_ok=True)
    (WEB / "img").mkdir(parents=True, exist_ok=True)

    fechas = [hoy - datetime.timedelta(days=d) for d in range(DIAS, 0, -1)]
    por_prov: dict[str, list[dict]] = {nombre: [] for _, nombre in PROVINCIAS}
    for fecha in fechas:
        st = _stations(_descarga(history_url(fecha), RAW / f"{fecha.isoformat()}.json"))
        for clave, nombre in PROVINCIAS:
            por_prov[nombre].append(day_summary(st, clave, RADIO_KM, DEPOSITO_L))

    # Precios actuales para el mapa: siempre frescos, nunca de cache.
    actual = get_json(current_url())
    mapa = _stations(actual)

    resumen = {
        "generado": datetime.datetime.now().isoformat(timespec="minutes"),
        "precios_mapa": actual.get("Fecha"),
        "semana": [fechas[0].isoformat(), fechas[-1].isoformat()],
        "n_estaciones": len(mapa),
        "radio_km": RADIO_KM,
        "deposito_l": DEPOSITO_L,
        "provincias": {nombre: _resumen_semana(dias) for nombre, dias in por_prov.items()},
        "fuente": "Ministerio para la Transición Ecológica y el Reto Demográfico — "
                  "Geoportal de Gasolineras (datos abiertos)",
    }
    (WEB / "data" / "summary.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")

    _escribir_mapa(mapa)

    from fuelfinder.charts import draw_all
    draw_all(resumen, WEB / "img")
    return resumen


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "--map-only":
        r = refresh_map()
        print(f"Mapa actualizado: {r['n_estaciones']} gasolineras, precios de {r['precios_mapa']}")
        return 0
    hoy = datetime.date.fromisoformat(argv[0]) if argv else datetime.date.today()
    r = build(hoy)
    v = r["provincias"]["Valencia"]
    print(f"Semana {r['semana'][0]} -> {r['semana'][1]} | precios del mapa: {r['precios_mapa']}")
    print(f"Valencia: +{100*v['gap_g95']:.1f} cts/L en gasolina 95 | "
          f"{v['pct_marca_con_lowcost']:.0f} % de marcas con low-cost a <{RADIO_KM} km | "
          f"{v['ahorro_deposito_diesel']:.2f} EUR por deposito")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
