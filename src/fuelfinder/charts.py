"""Diapositivas para el carrusel de LinkedIn (PNG 1080x1350), en estilo editorial.

Papel, tinta negra y rojo surtidor, con Source Serif 4 para titulares y cifras y
Source Sans 3 para el texto (ambas con licencia OFL, en assets/fonts). El rojo es
identidad visual y nunca codifica datos.

Colores de datos validados con el validador de la guia de visualizacion sobre el
papel #faf7f2: azul #2a78d6 / naranja #d95926 pasan todas las comprobaciones
(CVD dE 25.4, contraste >= 3:1). El naranja claro original (#eb6834) se quedaba
en 2,99:1 sobre el papel, por eso se usa un paso mas oscuro.
"""

from __future__ import annotations

import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

FUENTES = Path(__file__).resolve().parents[2] / "assets" / "fonts"
for _ttf in FUENTES.glob("*.ttf"):
    font_manager.fontManager.addfont(str(_ttf))

PAPER = "#faf7f2"
INK = "#1a1a1a"
TEXT_2 = "#4d4a45"
MUTED = "#6f6a62"
RULE = "#d9d3c7"
RED = "#d7261e"             # rojo surtidor: identidad, no datos
LOWCOST_C = "#2a78d6"       # serie 1 (azul)
MARCA_C = "#d95926"         # serie 2 (naranja, un paso mas oscuro para el papel)

SERIF = "Source Serif 4 Display"
SANS = "Source Sans 3"

W, H, DPI = 10.8, 13.5, 100
REPO = "github.com/nsorlop/fuelfinder-cv"

plt.rcParams.update({
    "font.family": [SANS, "Segoe UI", "DejaVu Sans"],
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "text.color": INK,
})

PROVS = ["Valencia", "Alicante", "Castellón"]
X0 = 0.075  # margen izquierdo comun


def _es(x: float, dec: int = 2) -> str:
    """Formato espanol: coma decimal."""
    return f"{x:.{dec}f}".replace(".", ",")


def _fecha_es(iso: str) -> str:
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
             "septiembre", "octubre", "noviembre", "diciembre"]
    d = datetime.date.fromisoformat(iso)
    return f"{d.day} de {meses[d.month - 1]}"


def _linea(fig, y: float, grosor: float, color: str = INK, x0: float = X0,
           x1: float = 1 - X0) -> None:
    fig.add_artist(plt.Rectangle((x0, y), x1 - x0, grosor, color=color,
                                 transform=fig.transFigure))


def _lienzo(n: int, total: int, antetitulo: str):
    """Cabecera tipo periodico: marca, numero de pagina, raya gruesa y antetitulo."""
    fig = plt.figure(figsize=(W, H), dpi=DPI)
    fig.add_artist(plt.Rectangle((X0, 0.944), 0.022, 0.018, color=RED,
                                 transform=fig.transFigure))
    fig.text(X0 + 0.034, 0.953, "FUELFINDER CV", fontsize=18, fontweight="bold",
             va="center", family=SANS)
    fig.text(1 - X0, 0.953, f"{n} / {total}", fontsize=17, color=MUTED, ha="right",
             va="center", family=SANS)
    _linea(fig, 0.928, 0.004)
    fig.text(X0, 0.895, antetitulo.upper(), fontsize=16, color=RED, fontweight="bold",
             family=SANS)
    _linea(fig, 0.068, 0.0012, RULE)
    fig.text(X0, 0.043, REPO, fontsize=15, color=MUTED, family=SANS)
    fig.text(1 - X0, 0.043, "Fuente: MITECO, datos abiertos", fontsize=15, color=MUTED,
             ha="right", family=SANS)
    return fig


def _titular(fig, lineas: list[str], y: float = 0.835, tam: int = 50, paso: float = 0.058):
    for linea in lineas:
        fig.text(X0, y, linea, fontsize=tam, fontweight="bold", family=SERIF)
        y -= paso
    return y


def _guardar(fig, ruta: Path) -> None:
    fig.savefig(ruta, dpi=DPI, facecolor=PAPER)
    plt.close(fig)


def portada(r: dict, ruta: Path, total: int) -> None:
    v = r["provincias"]["Valencia"]
    s = r["semana"]
    fig = _lienzo(1, total, "Datos · Comunitat Valenciana")
    _titular(fig, ["¿Cuánto te cuesta", "repostar en una", "gasolinera de marca?"], tam=60,
             paso=0.066)
    fig.text(X0, 0.50, f"+{_es(100 * v['gap_g95'], 0)} céntimos", fontsize=104,
             fontweight="bold", family=SERIF)
    _linea(fig, 0.468, 0.006, RED, x1=X0 + 0.16)
    fig.text(X0, 0.42, "por litro de gasolina 95 frente a una low-cost,", fontsize=27,
             color=TEXT_2)
    fig.text(X0, 0.385, "en la provincia de Valencia.", fontsize=27, color=TEXT_2)
    n = f"{r['n_estaciones']:,}".replace(",", ".")
    fig.text(X0, 0.26, f"{n} gasolineras, precios oficiales del {_fecha_es(s[0])}",
             fontsize=21, color=MUTED)
    fig.text(X0, 0.23, f"al {_fecha_es(s[1])} de 2026.", fontsize=21, color=MUTED)
    fig.text(X0, 0.13, "Desliza  →", fontsize=24, fontweight="bold")
    _guardar(fig, ruta)


def pesas(r: dict, ruta: Path, total: int) -> None:
    """Dumbbell: evita el eje de barras truncado, que exageraria la diferencia."""
    filas = sorted(PROVS, key=lambda p: r["provincias"][p]["gap_g95"])
    fig = _lienzo(2, total, "Las tres provincias")
    _titular(fig, ["La diferencia existe", "en todas partes"])
    fig.text(X0, 0.70, "Precio mediano de la gasolina 95, media de la semana (€/L)",
             fontsize=20, color=TEXT_2)

    ax = fig.add_axes([X0, 0.26, 1 - 2 * X0, 0.40])
    for y, prov in enumerate(filas):
        p = r["provincias"][prov]
        lo, ma = p["median_lowcost_g95"], p["median_marca_g95"]
        ax.plot([1.60, 2.15], [y - 0.42, y - 0.42], color=RULE, lw=1, zorder=0)
        ax.plot([lo, ma], [y, y], color=MUTED, lw=2, zorder=1)
        ax.scatter([lo], [y], s=560, color=LOWCOST_C, edgecolor=PAPER, lw=2.5, zorder=3)
        ax.scatter([ma], [y], s=560, color=MARCA_C, edgecolor=PAPER, lw=2.5, zorder=3)
        ax.text(lo - 0.013, y, _es(lo, 3), ha="right", va="center", fontsize=19,
                color=TEXT_2)
        ax.text(ma + 0.013, y, _es(ma, 3), ha="left", va="center", fontsize=19,
                color=TEXT_2)
        ax.text((lo + ma) / 2, y + 0.2, f"+{_es(100 * p['gap_g95'], 1)} cts",
                ha="center", va="bottom", fontsize=27, fontweight="bold", family=SERIF)
        ax.text(1.60, y, prov, ha="left", va="center", fontsize=25, fontweight="bold",
                family=SERIF)
    ax.set_xlim(1.60, 2.15)
    ax.set_ylim(-0.7, len(filas) - 0.25)
    ax.axis("off")

    # Leyenda siempre presente para 2 series: la identidad no va solo por color.
    fig.add_artist(plt.Circle((X0 + 0.012, 0.19), 0.011, color=LOWCOST_C,
                              transform=fig.transFigure))
    fig.text(X0 + 0.035, 0.19, "Low-cost", fontsize=21, va="center", color=TEXT_2)
    fig.add_artist(plt.Circle((X0 + 0.24, 0.19), 0.011, color=MARCA_C,
                              transform=fig.transFigure))
    fig.text(X0 + 0.263, 0.19, "Marca (Repsol, Cepsa, BP, Shell, Galp…)", fontsize=21,
             va="center", color=TEXT_2)
    _guardar(fig, ruta)


def cifra(ruta: Path, n: int, total: int, antetitulo: str, titulo: list[str],
          grande: str, explicacion: list[str]) -> None:
    """Numero protagonista: titular, cifra con serifa y explicacion debajo."""
    fig = _lienzo(n, total, antetitulo)
    _titular(fig, titulo)
    fig.text(X0, 0.47, grande, fontsize=190, fontweight="bold", family=SERIF)
    # La raya va por debajo de los trazos descendentes (la coma de "9,56"), no pegada.
    _linea(fig, 0.405, 0.006, RED, x1=X0 + 0.16)
    y = 0.345
    for linea in explicacion:
        fig.text(X0, y, linea, fontsize=27, color=TEXT_2)
        y -= 0.042
    _guardar(fig, ruta)


def metodologia(r: dict, ruta: Path, total: int) -> None:
    fig = _lienzo(total, total, "Metodología")
    _titular(fig, ["Cómo está hecho"])
    s = r["semana"]
    lineas = [
        ("Datos", "Precios oficiales del Ministerio para la Transición"),
        ("", "Ecológica. Datos abiertos, un registro por día."),
        ("Periodo", f"Del {_fecha_es(s[0])} al {_fecha_es(s[1])} de 2026 (7 días)."),
        ("Marca", "Repsol, Cepsa, Moeve, BP, Shell, Galp, Petronor."),
        ("Low-cost", "Plenergy, Ballenoil, Petroprix, GasExpress…"),
        ("Fuera", "Hipermercados e independientes: ante la duda,"),
        ("", "una gasolinera no entra en la comparación."),
        ("Distancia", f"{r['radio_km']} km en línea recta, no por carretera."),
        ("Depósito", f"{r['deposito_l']} litros de diésel."),
    ]
    y = 0.72
    for etiqueta, texto in lineas:
        if etiqueta:
            _linea(fig, y + 0.03, 0.0012, RULE)
            fig.text(X0, y, etiqueta, fontsize=21, fontweight="bold")
        fig.text(0.30, y, texto, fontsize=21, color=TEXT_2)
        y -= 0.044
    _linea(fig, 0.30, 0.004)
    fig.text(X0, 0.255, "Mapa con todas las gasolineras: la más barata,", fontsize=25,
             fontweight="bold", family=SERIF)
    fig.text(X0, 0.22, "la más cercana o la que más compensa, en tiempo", fontsize=25,
             fontweight="bold", family=SERIF)
    fig.text(X0, 0.185, "real. Enlace en el post.", fontsize=25, fontweight="bold",
             family=SERIF)
    fig.text(X0, 0.13, "Código abierto (MIT) y reproducible.", fontsize=21, color=TEXT_2)
    _guardar(fig, ruta)


def draw_all(r: dict, carpeta: Path) -> list[Path]:
    carpeta.mkdir(parents=True, exist_ok=True)
    v = r["provincias"]["Valencia"]
    total = 5
    rutas = [carpeta / f"slide_{i}.png" for i in range(1, total + 1)]
    portada(r, rutas[0], total)
    pesas(r, rutas[1], total)
    cifra(rutas[2], 3, total, "Cercanía", ["Dos de cada tres"],
          f"{_es(v['pct_marca_con_lowcost'], 0)} %",
          ["de las gasolineras de marca de Valencia",
           "tienen una low-cost a menos de 3 km.",
           "",
           f"{v['n']['marca']} de marca frente a {v['n']['lowcost']} low-cost."])
    cifra(rutas[3], 4, total, "Ahorro", ["Lo que te ahorras"],
          f"{_es(v['ahorro_deposito_diesel'], 2)} €",
          [f"por depósito de {r['deposito_l']} L de diésel, repostando",
           "en la low-cost más cercana (mediana).",
           "",
           "Aunque te desvíes 6 km, gastas menos",
           "de medio litro: compensa de sobra."])
    metodologia(r, rutas[4], total)
    return rutas
