"""Pruebas de integracion: Python + Prolog + Scala (requieren swipl, java y el JAR).

Ejecutar desde la carpeta python:   python -m pytest -q
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient  # noqa: E402

from api.app import app  # noqa: E402
from chatbot import texto as tx  # noqa: E402
from integracion import prolog_service as ps, scala_service  # noqa: E402
from modelos.carrito import Carrito, StockInsuficiente  # noqa: E402
from modelos.cliente import Cliente  # noqa: E402

client = TestClient(app)


# ── mejora 6: escape de atomos ──

@pytest.mark.parametrize("nombre", ["O'Brien", "x') , halt, ('", "back\\slash", "José Ñandú"])
def test_nombres_peligrosos_no_rompen_prolog(nombre):
    res = ps.recomendar(Cliente(nombre, 2000, "laptop", "estudio"))
    assert [p["codigo"] for p in res][:1] == ["laptop_acer_asp3"]


# ── mejora 7: catalogo unico, Prolog y Scala coinciden ──

def test_prolog_y_scala_tienen_el_mismo_catalogo():
    scala = {p["codigo"]: p for p in scala_service.catalogo()}
    for cat in tx.CATEGORIAS:
        for p in ps.catalogo_categoria(cat):
            s = scala[p["codigo"]]
            assert (p["precio"], p["categoria"], p["uso"], p["stock"]) == \
                   (s["precio"], s["categoria"], s["uso"], s["stock"]), p["codigo"]
    assert len(scala) == 42


# ── mejora 8: regla unica de IGV ──

def test_carrito_igv_y_restante():
    c = Carrito()
    c.agregar({"codigo": "a", "nombre": "A", "precio": 1250, "stock": 3}, 2)
    assert c.subtotal() == 2500
    assert c.igv() == 450
    assert c.total() == 2950
    assert c.restante(3000) == 50
    with pytest.raises(StockInsuficiente):
        c.agregar({"codigo": "a", "nombre": "A", "precio": 1250, "stock": 3}, 2)


# ── interpretacion de texto ──

def test_interpretacion_texto():
    assert tx.detectar_monto("S/ 2,500") == 2500
    assert tx.detectar_monto("unos 3k") == 3000
    assert tx.detectar_categoria("Busco audífonos") == "auricular"
    assert tx.detectar_categoria("Laptops") == "laptop"
    assert tx.detectar_uso("para la universidad") == "estudio"
    assert tx.es_sin_marca("me da igual")


# ── conversacion completa por HTTP ──

def _enviar(sid, texto=None, accion=None, valor=None):
    r = client.post("/api/chat", json={"sesion_id": sid, "texto": texto, "accion": accion, "valor": valor})
    assert r.status_code == 200, r.text
    return r.json()


def _tipos(resp):
    return [m["tipo"] for m in resp["mensajes"]]


def test_flujo_completo_chat():
    sid = client.post("/api/chat/sesion").json()["sesion_id"]
    _enviar(sid, "Ana")
    _enviar(sid, "2000 soles")
    _enviar(sid, accion="responder", valor="laptop")
    _enviar(sid, "para estudiar")
    r = _enviar(sid, "no")                       # sin marca -> recomendaciones
    assert r["perfil"]["presupuesto"] == 2000
    productos = next(m for m in r["mensajes"] if m["tipo"] == "productos")["productos"]
    assert productos and all(p["precio"] <= 2000 and "nombre" in p for p in productos)

    r = _enviar(sid, accion="agregar", valor="laptop_acer_asp3")
    assert [o["valor"] for o in r["opciones"] if o["accion"] == "cantidad"] == [1, 2, 3, 4, 5]
    r = _enviar(sid, "1")
    assert r["carrito"]["unidades"] == 1 and r["carrito"]["total"] == 1416

    r = _enviar(sid, "busco un celular samsung para trabajo de 3000")
    prods = next(m for m in r["mensajes"] if m["tipo"] == "productos")["productos"]
    assert [p["codigo"] for p in prods] == ["cel_samsung_s23"]

    r = _enviar(sid, accion="reportes")
    assert "reporte" in _tipos(r)
    r = _enviar(sid, accion="catalogo")
    assert len(next(m for m in r["mensajes"] if m["tipo"] == "productos")["productos"]) == 42

    r = _enviar(sid, accion="finalizar")
    assert "carrito" in _tipos(r)
    r = _enviar(sid, "sí")
    assert r["carrito"]["unidades"] == 0


def test_eliminar_del_carrito():
    sid = client.post("/api/chat/sesion").json()["sesion_id"]
    for paso in ["Luis", "900", "tablet", "estudio", "ninguna"]:
        _enviar(sid, paso)
    _enviar(sid, accion="agregar", valor="tab_lenovo_m10")
    _enviar(sid, accion="cantidad", valor=2)
    r = _enviar(sid, accion="eliminar", valor="tab_lenovo_m10")
    assert r["carrito"]["unidades"] == 0


def test_endpoints_rest():
    assert len(client.get("/api/catalogo", params={"categoria": "monitor"}).json()) == 6
    r = client.post("/api/recomendaciones",
                    json={"presupuesto": 1000, "categoria": "laptop", "uso": "estudio"}).json()
    assert r["es_alternativa"] is True and r["productos"][0]["codigo"] == "laptop_acer_asp3"
    assert client.post("/api/chat", json={"sesion_id": "nope"}).status_code == 404
