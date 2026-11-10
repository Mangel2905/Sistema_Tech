"""Inventario compartido: descuenta stock al confirmar una compra.

El stock actual se guarda en datos/stock.csv. Prolog (consultas.pl) y Scala
(StockService) lo leen en cada ejecucion, asi que despues de una compra:
  - Prolog deja de recomendar lo que se agoto (regla disponible/1),
  - Scala muestra el stock nuevo en catalogo y reportes,
  - el carrito no permite agregar mas unidades de las que quedan.

Uso por consola para volver al stock inicial:
    python -m integracion.inventario --reiniciar
"""
import csv
import os
import sys
import tempfile
import threading

from integracion import config, scala_service

_lock = threading.Lock()


class CompraRechazada(Exception):
    """El stock cambio desde que se armo el carrito.

    faltantes: [{'codigo', 'nombre', 'pedido', 'disponible'}]
    """

    def __init__(self, faltantes):
        self.faltantes = faltantes
        detalle = ", ".join(f"{f['nombre']} (pediste {f['pedido']}, quedan {f['disponible']})"
                            for f in faltantes)
        super().__init__(f"Stock insuficiente: {detalle}")


def stock_actual():
    """{codigo: stock} leido desde Scala (que aplica el CSV sobre el stock inicial)."""
    return {p["codigo"]: p["stock"] for p in scala_service.catalogo()}


def verificar(items):
    """Lista de faltantes para los items [{'codigo','cantidad','nombre'}] segun el stock actual."""
    actual = stock_actual()
    faltantes = []
    for it in items:
        disponible = actual.get(it["codigo"], 0)
        if it["cantidad"] > disponible:
            faltantes.append({"codigo": it["codigo"], "nombre": it.get("nombre", it["codigo"]),
                              "pedido": it["cantidad"], "disponible": max(disponible, 0)})
    return faltantes


def registrar_compra(items):
    """Descuenta del stock las cantidades compradas. Todo o nada.

    Lanza CompraRechazada si algun producto ya no tiene stock suficiente
    (por ejemplo, porque otro cliente compro antes). Devuelve el stock nuevo.
    """
    with _lock:
        scala_service.invalidar_cache()      # leer el stock mas reciente
        faltantes = verificar(items)
        if faltantes:
            raise CompraRechazada(faltantes)
        nuevo = stock_actual()
        for it in items:
            nuevo[it["codigo"]] -= it["cantidad"]
        _guardar(nuevo)
        scala_service.invalidar_cache()
        return nuevo


def reiniciar():
    """Vuelve al stock inicial de hechos.pl / CatalogoService.scala."""
    with _lock:
        try:
            os.remove(config.ruta_stock())
        except FileNotFoundError:
            pass
        scala_service.invalidar_cache()


def _guardar(stock):
    """Escritura atomica: archivo temporal + reemplazo, para no dejar un CSV a medias."""
    ruta = config.ruta_stock()
    carpeta = os.path.dirname(ruta)
    os.makedirs(carpeta, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=carpeta, prefix=".stock-", suffix=".csv")
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["codigo", "stock"])
            for codigo in sorted(stock):
                w.writerow([codigo, stock[codigo]])
        os.replace(tmp, ruta)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


if __name__ == "__main__":
    if "--reiniciar" in sys.argv:
        reiniciar()
        print("Stock reiniciado a los valores iniciales.")
    else:
        print(__doc__)
