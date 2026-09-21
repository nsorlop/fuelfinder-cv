import ssl

import pytest

from fuelfinder.analyze import day_summary, median_price, nearby_savings
from fuelfinder.brands import LOWCOST, MARCA, OTRAS
from fuelfinder.fetch import history_url, ssl_context
from fuelfinder.geo import km
from fuelfinder.normalize import Station, parse_price, parse_station


# ---------- normalize ----------

@pytest.mark.parametrize("texto, esperado", [
    ("1,979", 1.979), ("2,045", 2.045), ("1.5", 1.5), ("  1,799 ", 1.799),
])
def test_parse_price_handles_spanish_decimal_comma(texto, esperado):
    assert parse_price(texto) == pytest.approx(esperado)


@pytest.mark.parametrize("texto", ["", "   ", None])
def test_parse_price_empty_is_none(texto):
    assert parse_price(texto) is None


def _raw(**cambios):
    base = {
        "IDEESS": "123", "Rótulo": "REPSOL", "Municipio": "Valencia",
        "Provincia": "VALENCIA / VALÈNCIA", "Dirección": "CALLE X, 1", "Horario": "L-D: 24H",
        "Latitud": "39,4699", "Longitud (WGS84)": "-0,3763",
        "Precio Gasolina 95 E5": "1,999", "Precio Gasoleo A": "1,899",
    }
    base.update(cambios)
    return base


def test_parse_station_builds_a_station():
    s = parse_station(_raw())
    assert s.id == "123"
    assert s.grupo == MARCA
    assert s.lat == pytest.approx(39.4699)
    assert s.lon == pytest.approx(-0.3763)
    assert s.g95 == pytest.approx(1.999)
    assert s.diesel == pytest.approx(1.899)


def test_parse_station_without_coordinates_is_none():
    assert parse_station(_raw(Latitud="")) is None


def test_parse_station_keeps_missing_prices_as_none():
    s = parse_station(_raw(**{"Precio Gasolina 95 E5": ""}))
    assert s.g95 is None
    assert s.diesel == pytest.approx(1.899)


# ---------- geo ----------

def test_km_valencia_madrid_is_about_302_km():
    assert km((39.4699, -0.3763), (40.4168, -3.7038)) == pytest.approx(302, abs=3)


def test_km_same_point_is_zero():
    assert km((39.47, -0.37), (39.47, -0.37)) == pytest.approx(0)


# ---------- fetch (sin red) ----------

def test_ssl_context_keeps_certificate_verification():
    # El servidor del Ministerio solo acepta cifrados antiguos. El arreglo baja
    # el nivel de cifrado, pero NUNCA puede desactivar la verificacion.
    ctx = ssl_context()
    assert ctx.verify_mode == ssl.CERT_REQUIRED
    assert ctx.check_hostname is True


def test_history_url_uses_ministry_date_format():
    import datetime
    url = history_url(datetime.date(2026, 9, 14), ccaa="10")
    assert url.endswith("/EstacionesTerrestresHist/FiltroCCAA/14-09-2026/10")


# ---------- analyze ----------

def _st(grupo, lat, lon, g95=None, diesel=None, prov="VALENCIA / VALÈNCIA"):
    return Station(id=f"{grupo}{lat}{lon}", rotulo=grupo, grupo=grupo, municipio="X",
                   provincia=prov, direccion="", horario="", lat=lat, lon=lon,
                   g95=g95, diesel=diesel)


def test_median_price_by_group_ignores_missing_prices():
    st = [_st(MARCA, 39, 0, g95=2.0), _st(MARCA, 39, 0, g95=2.2), _st(MARCA, 39, 0, g95=None),
          _st(LOWCOST, 39, 0, g95=1.8)]
    assert median_price(st, MARCA, "g95") == pytest.approx(2.1)
    assert median_price(st, LOWCOST, "g95") == pytest.approx(1.8)


def test_median_price_of_empty_group_is_none():
    assert median_price([_st(MARCA, 39, 0, g95=2.0)], LOWCOST, "g95") is None


def test_nearby_savings_uses_the_cheapest_lowcost_within_radius():
    marca = _st(MARCA, 39.0, 0.0, diesel=2.00)
    cerca_cara = _st(LOWCOST, 39.01, 0.0, diesel=1.90)     # ~1,1 km
    cerca_barata = _st(LOWCOST, 39.0, 0.01, diesel=1.80)   # ~0,9 km
    lejos = _st(LOWCOST, 39.5, 0.0, diesel=1.50)           # ~55 km: fuera
    ahorros, con_cercana, total = nearby_savings([marca, cerca_cara, cerca_barata, lejos], "diesel", 3)
    assert total == 1 and con_cercana == 1
    assert ahorros == [pytest.approx(0.20)]


def test_nearby_savings_ignores_otras_and_marca_without_lowcost():
    marca = _st(MARCA, 39.0, 0.0, diesel=2.00)
    otra = _st(OTRAS, 39.0, 0.001, diesel=1.00)   # barata, pero no es low-cost
    ahorros, con_cercana, total = nearby_savings([marca, otra], "diesel", 3)
    assert (ahorros, con_cercana, total) == ([], 0, 1)


def test_day_summary_reports_gap_and_tank_saving():
    st = [_st(MARCA, 39.0, 0.0, g95=2.0, diesel=2.0),
          _st(LOWCOST, 39.0, 0.01, g95=1.75, diesel=1.8)]
    r = day_summary(st, provincia="VALENCIA / VALÈNCIA", radio_km=3, deposito_l=50)
    assert r["n"][MARCA] == 1 and r["n"][LOWCOST] == 1
    assert r["gap_g95"] == pytest.approx(0.25)
    assert r["pct_marca_con_lowcost"] == pytest.approx(100)
    assert r["ahorro_deposito_diesel"] == pytest.approx(10.0)


def test_day_summary_filters_by_province():
    st = [_st(MARCA, 39.0, 0.0, g95=2.0, prov="ALICANTE"),
          _st(LOWCOST, 39.0, 0.0, g95=1.0, prov="ALICANTE")]
    r = day_summary(st, provincia="VALENCIA / VALÈNCIA", radio_km=3, deposito_l=50)
    assert r["n"][MARCA] == 0
    assert r["gap_g95"] is None
