"""Configuracion compartida por los puentes hacia Prolog y Scala."""
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))


def ruta_stock():
    """CSV con el stock actual (codigo,stock). Se puede cambiar con TECHPOS_STOCK."""
    return os.environ.get("TECHPOS_STOCK") or os.path.join(REPO, "datos", "stock.csv")


def entorno():
    """Variables de entorno para swipl y java: les indica que archivo de stock leer."""
    env = dict(os.environ)
    env["TECHPOS_STOCK"] = ruta_stock()
    return env
