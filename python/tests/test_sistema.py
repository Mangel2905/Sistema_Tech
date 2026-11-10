"""Pruebas de integracion: Python + Prolog + Scala (requieren swipl, java y el JAR).

Ejecutar desde la carpeta python:   python -m pytest -q
"""
import os
import sys
import tempfile

import pytest

# Las pruebas compran productos: usan un archivo de stock temporal, nunca datos/stock.csv
os.environ["TECHPOS_STOCK"] = os.path.join(tempfile.mkdtemp(prefix="techpos-test-"), "stock.csv")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient  # noqa: E402

from api.app import app  # noqa: E402
from chatbot import texto as tx  # noqa: E402
from integracion import inventario, prolog_service as ps, scala_service  # noqa: E402
from modelos.carrito import Carrito, StockInsuficiente  # noqa: E402
from modelos.cliente import Cliente  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def stock_inicial():
    """Cada prueba empieza con el stock inicial."""
    inventario.reiniciar()
    yield
    inventario.reiniciar()


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


# ── descuento de stock al comprar ──

def _sesion_registrada(nombre="Ana", presupuesto="9000", categoria="laptop", uso="estudio"):
    sid = client.post("/api/chat/sesion").json()["sesion_id"]
    for paso in [nombre, presupuesto, categoria, uso, "ninguna"]:
        _enviar(sid, paso)
    return sid


def _avisos(resp):
    return " | ".join(m["texto"] for m in resp["mensajes"] if m["tipo"] == "aviso")


def test_compra_descuenta_stock_en_prolog_y_scala():
    sid = _sesion_registrada()
    _enviar(sid, accion="agregar", valor="laptop_acer_asp3")
    _enviar(sid, accion="cantidad", valor=2)
    _enviar(sid, accion="finalizar")
    r = _enviar(sid, accion="confirmar")
    assert "Compra realizada" in _avisos(r)

    assert scala_service.producto("laptop_acer_asp3")["stock"] == 5           # Scala
    assert ps.verificar_stock("laptop_acer_asp3") == {"disponible": True, "stock": 5}   # Prolog
    assert os.path.exists(os.environ["TECHPOS_STOCK"])


def test_producto_agotado_no_se_recomienda_ni_se_agrega():
    inventario.registrar_compra([{"codigo": "laptop_dell_ins15", "cantidad": 2, "nombre": "Dell"}])

    # Prolog ya no lo recomienda (unica laptop de trabajo)
    assert ps.recomendar(Cliente("x", 3000, "laptop", "trabajo")) == []
    assert ps.verificar_stock("laptop_dell_ins15")["disponible"] is False
    # Scala lo marca agotado y lo saca del catalogo por categoria
    assert scala_service.producto("laptop_dell_ins15")["stock"] == 0
    assert "laptop_dell_ins15" not in [p["codigo"] for p in scala_service.catalogo("laptop")]
    assert [p["codigo"] for p in scala_service.reportes()["agotados"]] == ["laptop_dell_ins15"]

    # El chat no permite agregarlo
    sid = _sesion_registrada()
    r = _enviar(sid, accion="agregar", valor="laptop_dell_ins15")
    assert "agotado" in _avisos(r) and r["carrito"]["unidades"] == 0
    # El carrito tampoco
    with pytest.raises(StockInsuficiente):
        Carrito().agregar(scala_service.producto("laptop_dell_ins15"), 1)
    # Y una compra directa se rechaza sin tocar el stock
    with pytest.raises(inventario.CompraRechazada):
        inventario.registrar_compra([{"codigo": "laptop_dell_ins15", "cantidad": 1}])
    assert scala_service.producto("laptop_dell_ins15")["stock"] == 0


def test_carrito_se_ajusta_si_otro_cliente_compra_antes():
    sid = _sesion_registrada(categoria="tablet", uso="trabajo")
    _enviar(sid, accion="agregar", valor="tab_samsung_s7")      # stock 2
    _enviar(sid, accion="cantidad", valor=2)

    inventario.registrar_compra([{"codigo": "tab_samsung_s7", "cantidad": 1}])   # otro cliente

    r = _enviar(sid, accion="finalizar")
    assert "Solo quedan 1" in _avisos(r) and r["carrito"]["unidades"] == 1
    _enviar(sid, accion="confirmar")
    assert scala_service.producto("tab_samsung_s7")["stock"] == 0


def test_confirmacion_rechazada_si_el_stock_cambia_en_el_ultimo_momento():
    sid = _sesion_registrada()
    _enviar(sid, accion="agregar", valor="laptop_acer_asp3")    # stock 7
    _enviar(sid, accion="cantidad", valor=2)
    _enviar(sid, accion="finalizar")                            # resumen mostrado

    inventario.registrar_compra([{"codigo": "laptop_acer_asp3", "cantidad": 6}])   # quedan 1

    r = _enviar(sid, accion="confirmar")
    assert "no se cobró nada" in _avisos(r)
    assert r["carrito"]["unidades"] == 1
    assert scala_service.producto("laptop_acer_asp3")["stock"] == 1   # nada descontado
    r = _enviar(sid, accion="confirmar")
    assert "Compra realizada" in _avisos(r)
    assert scala_service.producto("laptop_acer_asp3")["stock"] == 0
