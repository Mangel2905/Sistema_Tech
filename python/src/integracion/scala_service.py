"""Puente Python -> Scala (JAR generado con `sbt assembly`).

Scala es la FUENTE UNICA del catalogo: nombres comerciales, marcas, precios
y stock se leen de aqui (comando `json`) en lugar de duplicarlos en Python.
"""
import json
import os
import shutil
import subprocess
from functools import lru_cache

from integracion import config

SCALA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scala"))
JAR_PATH = os.path.join(SCALA_DIR, "target", "out", "jvm", "scala-2.13.12", "sistema-tech",
                        "Sistema-Tech-assembly-0.1.0.jar")


class ScalaError(RuntimeError):
    """Java/JAR no disponible o el comando Scala fallo."""


def _java_cmd():
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        candidato = os.path.join(java_home, "bin", "java.exe" if os.name == "nt" else "java")
        if os.path.exists(candidato):
            return candidato
    return shutil.which("java")


def _ejecutar(args):
    if not os.path.exists(JAR_PATH):
        raise ScalaError("JAR no encontrado. Corre 'sbt assembly' en la carpeta scala.")
    java = _java_cmd()
    if java is None:
        raise ScalaError("Java no encontrado en el PATH.")
    try:
        result = subprocess.run(
            [java, "-jar", JAR_PATH] + list(args),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            cwd=SCALA_DIR,
            env=config.entorno(),
        )
    except subprocess.TimeoutExpired as e:
        raise ScalaError("Scala tardo demasiado.") from e
    if result.returncode != 0:
        raise ScalaError(result.stderr.strip() or f"Scala termino con codigo {result.returncode}")
    return result.stdout


def _json(args):
    salida = _ejecutar(args).strip()
    try:
        return json.loads(salida)
    except json.JSONDecodeError as e:
        raise ScalaError(f"Respuesta de Scala no es JSON valido: {salida[:120]}") from e


# ── datos estructurados (usados por el chatbot web y la consola) ──

@lru_cache(maxsize=None)
def _catalogo_cache(categoria):
    args = ["json"] if categoria is None else ["json", categoria]
    return tuple(_json(args))


def catalogo(categoria=None):
    """Lista de productos (dicts). Con categoria: solo esa categoria y con stock."""
    return [dict(p) for p in _catalogo_cache(categoria)]


@lru_cache(maxsize=1)
def _indice():
    return {p["codigo"]: p for p in _catalogo_cache(None)}


def producto(codigo):
    """Producto completo por codigo, o None si no existe."""
    p = _indice().get(codigo)
    return dict(p) if p else None


@lru_cache(maxsize=1)
def reportes():
    """{'stockBajo': [...], 'agotados': [...], 'resumen': [{'categoria', 'cantidad', 'masCaro', 'masBarato'}]}"""
    return _json(["reporte-json"])


def invalidar_cache():
    """Olvida catalogo y reportes en memoria (se llama cuando cambia el stock)."""
    _catalogo_cache.cache_clear()
    _indice.cache_clear()
    reportes.cache_clear()


# ── salida en texto (modo consola original) ──

def listar_todo():
    return _ejecutar(["listar"])


def listar_categoria(categoria):
    return _ejecutar(["listar", categoria])


def reporte():
    return _ejecutar(["reporte"])
