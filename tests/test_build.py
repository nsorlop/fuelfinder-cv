from fuelfinder.build import merge_map_refresh


def _resumen():
    return {
        "generado": "2026-09-21T14:33",
        "precios_mapa": "21/09/2026 14:33:42",
        "n_estaciones": 1315,
        "semana": ["2026-09-14", "2026-09-20"],
        "provincias": {"Valencia": {"gap_g95": 0.269}},
    }


def test_map_refresh_updates_only_the_map_fields():
    nuevo = merge_map_refresh(_resumen(), "22/09/2026 09:00:00", 1316, "2026-09-22T09:02")
    assert nuevo["precios_mapa"] == "22/09/2026 09:00:00"
    assert nuevo["n_estaciones"] == 1316
    assert nuevo["mapa_actualizado"] == "2026-09-22T09:02"


def test_map_refresh_never_touches_the_weekly_analysis():
    # Las cifras de la semana son las del post y el carrusel: no pueden cambiar solas.
    original = _resumen()
    nuevo = merge_map_refresh(original, "22/09/2026 09:00:00", 1316, "2026-09-22T09:02")
    assert nuevo["semana"] == original["semana"]
    assert nuevo["provincias"] == original["provincias"]
    assert nuevo["generado"] == original["generado"]


def test_map_refresh_does_not_mutate_its_input():
    original = _resumen()
    merge_map_refresh(original, "22/09/2026 09:00:00", 1316, "2026-09-22T09:02")
    assert original["precios_mapa"] == "21/09/2026 14:33:42"
