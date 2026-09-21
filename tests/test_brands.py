import pytest

from fuelfinder.brands import HIPER, LOWCOST, MARCA, OTRAS, classify


@pytest.mark.parametrize("rotulo", [
    "REPSOL", "CEPSA", "MOEVE", "BP", "SHELL", "GALP", "PETRONOR",
    "BP OIL ESPAÑA", "BP ALFAZ DEL PI", "GALP - AMERICAN PETROL", "Repsol",
])
def test_major_brands_are_marca(rotulo):
    assert classify(rotulo) == MARCA


@pytest.mark.parametrize("rotulo", [
    "PLENERGY", "PLENOIL", "BALLENOIL", "PETROPRIX", "GASEXPRESS", "BONAREA",
    "AVANZA LOW COST", "LOW COST 24H", "bonÀrea",
])
def test_lowcost_chains_are_lowcost(rotulo):
    assert classify(rotulo) == LOWCOST


@pytest.mark.parametrize("rotulo", ["CARREFOUR", "ALCAMPO"])
def test_hypermarkets_are_separate(rotulo):
    assert classify(rotulo) == HIPER


@pytest.mark.parametrize("rotulo", [
    "CAMPSA EXPRESS",   # marca barata de Repsol: ambigua, fuera de la comparacion
    "Q8", "TAMOIL", "ENI", "HAM", "(SIN RÓTULO)", "", "STELS", "GASOLWIN",
])
def test_ambiguous_or_independent_are_otras(rotulo):
    assert classify(rotulo) == OTRAS


def test_brand_names_are_matched_as_whole_words():
    # "BP" no puede colarse dentro de otra palabra.
    assert classify("BPX ENERGIA") == OTRAS
    assert classify("GASOLINERA SHELLAC") == OTRAS


def test_none_is_otras():
    assert classify(None) == OTRAS
