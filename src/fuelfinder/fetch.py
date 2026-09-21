"""Descarga de precios desde el servicio REST del Ministerio."""

from __future__ import annotations

import datetime
import json
import ssl
import urllib.request

BASE = ("https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/"
        "PreciosCarburantes")
CCAA_COMUNITAT_VALENCIANA = "10"


def ssl_context() -> ssl.SSLContext:
    """Contexto TLS compatible con el servidor del Ministerio.

    El servidor solo negocia cifrados que OpenSSL 3 rechaza con su nivel de
    seguridad por defecto (2), y corta la conexion en el saludo TLS. Se baja
    el NIVEL DE CIFRADO a 1. La verificacion del certificado y del nombre del
    host se mantiene intacta: desactivarla (verify=False) seria un fallo de
    seguridad, no un arreglo.
    """
    ctx = ssl.create_default_context()
    ctx.set_ciphers("DEFAULT@SECLEVEL=1")
    return ctx


def current_url(ccaa: str = CCAA_COMUNITAT_VALENCIANA) -> str:
    return f"{BASE}/EstacionesTerrestres/FiltroCCAA/{ccaa}"


def history_url(fecha: datetime.date, ccaa: str = CCAA_COMUNITAT_VALENCIANA) -> str:
    return f"{BASE}/EstacionesTerrestresHist/FiltroCCAA/{fecha.strftime('%d-%m-%Y')}/{ccaa}"


def get_json(url: str, timeout: float = 120) -> dict:
    peticion = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(peticion, context=ssl_context(), timeout=timeout) as r:
        return json.load(r)
