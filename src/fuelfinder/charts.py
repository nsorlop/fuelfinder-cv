"""Diapositivas para el carrusel de LinkedIn (PNG 1080x1350).

Paleta validada con el validador de la guia de visualizacion sobre la superficie
#15171c: azul/naranja pasan todas las comprobaciones (CVD dE 26.8, contraste >= 3:1).
El ambar es acento de marca: nunca codifica datos.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SURFACE = "#15171c"
TEXT = "#ffffff"
TEXT_2 = "#c3c2b7"
MUTED = "#8d9099"
GRID = "#2a2d35"
ACCENT = "#f0a027"          # marca personal, solo decorativo
LOWCOST_C = "#3987e5"       # serie 1 (azul)
MARCA_C = "#d95926"         # serie 2 (naranja)

W, H, DPI = 10.8, 13.5, 100
REPO = "github.com/nsorlop/fuelfinder-cv"

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "text.color": TEXT, "axes.edgecolor": GRID,
})

PROVS = ["Valencia", "Alicante", "Castellón"]


def _es(x: float, dec: int = 2) -> str:
    """Formato espanol: coma decimal."""
    return f"{x:.{dec}f}".replace(".", ",")


def _fecha_es(iso: str) -> str:
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} de {meses[d.month - 1]}"


def _lienzo(n: int, total: int):
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.add_artist(plt.Rectangle((0.07, 0.935), 0.09, 0.006, color=ACCENT,
                                 transform=fig.transFigure))
    fig.text(0.07, 0.955, "FUELFINDER CV", color=TEXT_2, fontsize=15,
             fontweight="bold")
    fig.text(0.93, 0.955, f"{n}/{total}", color=MUTED, fontsize=15, ha="right")
    fig.text(0.07, 0.035, REPO, color=MUTED, fontsize=14)
    return fig


def _guardar(fig, ruta: Path) -> None:
    fig.savefig(ruta, dpi=DPI, facecolor=SURFACE)
    plt.close(fig)


def portada(r: dict, ruta: Path, total: int) -> None:
    v = r["provincias"]["Valencia"]
    fig = _lienzo(1, total)
    fig.text(0.07, 0.80, "¿Cuánto te cuesta", fontsize=58, fontweight="bold")
    fig.text(0.07, 0.735, "repostar en una", fontsize=58, fontweight="bold")
    fig.text(0.07, 0.67, "gasolinera de marca?", fontsize=58, fontweight="bold")
    fig.text(0.07, 0.52, f"+{_es(100 * v['gap_g95'], 0)} céntimos", fontsize=96,
             fontweight="bold")
    fig.text(0.07, 0.465, "por litro de gasolina 95 frente a una low-cost",
             fontsize=24, color=TEXT_2)
    fig.text(0.07, 0.435, "en la provincia de Valencia", fontsize=24, color=TEXT_2)
    s = r["semana"]
    fig.text(0.07, 0.30, f"{r['n_estaciones']:,} gasolineras de la Comunitat Valenciana.".replace(",", "."), fontsize=21,
             color=MUTED)
    fig.text(0.07, 0.27, f"Precios oficiales del {_fecha_es(s[0])} al {_fecha_es(s[1])}.",
             fontsize=21, color=MUTED)
    fig.text(0.07, 0.14, "Desliza  →", fontsize=24, color=TEXT_2, fontweight="bold")
    _guardar(fig, ruta)


def pesas(r: dict, ruta: Path, total: int) -> None:
    """Dumbbell: evita el eje de barras truncado, que exageraria la diferencia."""
    filas = sorted(PROVS, key=lambda p: r["provincias"][p]["gap_g95"])
    fig = _lienzo(2, total)
    fig.text(0.07, 0.855, "La diferencia existe", fontsize=46, fontweight="bold")
    fig.text(0.07, 0.805, "en las tres provincias", fontsize=46, fontweight="bold")
    fig.text(0.07, 0.765, "Precio mediano de la gasolina 95, media de la semana (€/L)",
             fontsize=19, color=TEXT_2)

    ax = fig.add_axes([0.07, 0.25, 0.86, 0.46])
    for y, prov in enumerate(filas):
        p = r["provincias"][prov]
        lo, ma = p["median_lowcost_g95"], p["median_marca_g95"]
        ax.plot([lo, ma], [y, y], color=MUTED, lw=2, zorder=1)
        ax.scatter([lo], [y], s=520, color=LOWCOST_C, edgecolor=SURFACE, lw=2, zorder=3)
        ax.scatter([ma], [y], s=520, color=MARCA_C, edgecolor=SURFACE, lw=2, zorder=3)
        ax.text(lo - 0.012, y, _es(lo, 3), ha="right", va="center", fontsize=19,
                color=TEXT_2)
        ax.text(ma + 0.012, y, _es(ma, 3), ha="left", va="center", fontsize=19,
                color=TEXT_2)
        ax.text((lo + ma) / 2, y + 0.24, f"+{_es(100 * p['gap_g95'], 1)} cts",
                ha="center", va="bottom", fontsize=24, fontweight="bold", color=TEXT)
        ax.text(1.60, y, prov, ha="left", va="center", fontsize=24, fontweight="bold",
                color=TEXT)
    ax.set_xlim(1.60, 2.15)
    ax.set_ylim(-0.7, len(filas) - 0.2)
    ax.axis("off")

    # Leyenda siempre presente para 2 series (la identidad no va solo por color).
    fig.add_artist(plt.Circle((0.10, 0.19), 0.012, color=LOWCOST_C,
                              transform=fig.transFigure))
    fig.text(0.125, 0.19, "Low-cost", fontsize=21, va="center", color=TEXT_2)
    fig.add_artist(plt.Circle((0.36, 0.19), 0.012, color=MARCA_C,
                              transform=fig.transFigure))
    fig.text(0.385, 0.19, "Marca (Repsol, Cepsa, BP, Shell, Galp…)", fontsize=21,
             va="center", color=TEXT_2)
    _guardar(fig, ruta)


def cifra(ruta: Path, n: int, total: int, titulo: str, grande: str,
          explicacion: list[str]) -> None:
    """Numero protagonista: titulo de contexto, cifra y explicacion debajo."""
    fig = _lienzo(n, total)
    fig.text(0.07, 0.80, titulo, fontsize=46, fontweight="bold")
    fig.text(0.07, 0.53, grande, fontsize=180, fontweight="bold", color=TEXT)
    fig.add_artist(plt.Rectangle((0.07, 0.475), 0.20, 0.008, color=ACCENT,
                                 transform=fig.transFigure))
    y = 0.40
    for linea in explicacion:
        fig.text(0.07, y, linea, fontsize=27, color=TEXT_2)
        y -= 0.042
    _guardar(fig, ruta)


def metodologia(r: dict, ruta: Path, total: int) -> None:
    fig = _lienzo(total, total)
    fig.text(0.07, 0.83, "Cómo está hecho", fontsize=46, fontweight="bold")
    s = r["semana"]
    lineas = [
        ("Datos", "Precios oficiales del Ministerio para la Transición"),
        ("", "Ecológica. Datos abiertos, un registro por día."),
        ("Periodo", f"{_fecha_es(s[0])} – {_fecha_es(s[1])} de 2026 (7 días)."),
        ("Marca", "Repsol, Cepsa, Moeve, BP, Shell, Galp, Petronor."),
        ("Low-cost", "Plenergy, Ballenoil, Petroprix, GasExpress…"),
        ("Fuera", "Hipermercados e independientes: ante la duda,"),
        ("", "una gasolinera no entra en la comparación."),
        ("Distancia", f"{r['radio_km']} km en línea recta, no por carretera."),
        ("Depósito", f"{r['deposito_l']} litros de diésel."),
    ]
    y = 0.74
    for etiqueta, texto in lineas:
        if etiqueta:
            fig.text(0.07, y, etiqueta, fontsize=21, fontweight="bold", color=TEXT)
        fig.text(0.30, y, texto, fontsize=21, color=TEXT_2)
        y -= 0.045
    fig.text(0.07, 0.25, "Mapa con todas las gasolineras y la más", fontsize=26,
             fontweight="bold")
    fig.text(0.07, 0.21, "barata cerca de ti: enlace en el post.", fontsize=26,
             fontweight="bold")
    fig.text(0.07, 0.15, "Código abierto (MIT) y reproducible.", fontsize=21, color=TEXT_2)
    _guardar(fig, ruta)


def draw_all(r: dict, carpeta: Path) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    v = r["provincias"]["Valencia"]
    total = 5
    rutas = [carpeta / f"slide_{i}.png" for i in range(1, total + 1)]
    portada(r, rutas[0], total)
    pesas(r, rutas[1], total)
    pct = v["pct_marca_con_lowcost"]
    cifra(rutas[2], 3, total, "Dos de cada tres", f"{_es(pct, 0)} %",
          ["de las gasolineras de marca de Valencia",
           "tienen una low-cost a menos de 3 km.",
           "",
           f"{v['n']['marca']} de marca frente a {v['n']['lowcost']} low-cost."])
    cifra(rutas[3], 4, total, "Lo que te ahorras", f"{_es(v['ahorro_deposito_diesel'], 2)} €",
          [f"por depósito de {r['deposito_l']} L de diésel, repostando",
           "en la low-cost más cercana (mediana).",
           "",
           "Aunque te desvíes 6 km, gastas menos",
           "de medio litro: compensa de sobra."])
    metodologia(r, rutas[4], total)
    return rutas
