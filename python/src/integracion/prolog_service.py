"""Puente Python -> Prolog (SWI-Prolog por linea de comandos).

Cada consulta lanza `swipl` con un objetivo de consultas.pl y lee su salida,
una linea por producto con el formato  codigo|precio|categoria|uso|stock.
"""
import os
import shutil
import subprocess

BASE = os.path.dirname(__file__)
CONSULTAS = os.path.abspath(os.path.join(BASE, "../../../prolog/consultas.pl"))


class PrologError(RuntimeError):
    """Prolog no esta disponible o la consulta fallo."""


def _swipl_cmd():
    cmd = shutil.which("swipl")
    if cmd:
        return cmd
    posibles = [
        r"C:\Program Files\swipl\bin\swipl.exe",
        r"C:\Program Files (x86)\swipl\bin\swipl.exe",
        r"C:\swipl\bin\swipl.exe",
    ]
    for ruta in posibles:
        if os.path.exists(ruta):
            return ruta
    return None


def atomo(valor):
    """Convierte cualquier texto en un atomo Prolog entre comillas simples.

    Escapa la barra invertida y la comilla simple, de modo que entradas como
    "O'Brien" o "a') , halt, ('" no rompen ni alteran el objetivo.
    """
    texto = str(valor).replace("\\", "\\\\").replace("'", "\\'")
    texto = texto.replace("\n", " ").replace("\r", " ")
    return f"'{texto}'"


def entero(valor):
    """Garantiza que el valor sea un entero (nunca texto libre) en el objetivo."""
    return str(int(valor))


def _ejecutar(goal):
    swipl = _swipl_cmd()
    if swipl is None:
        raise PrologError("swipl no encontrado. Instala SWI-Prolog y agregalo al PATH.")
    try:
        result = subprocess.run(
            [swipl, "-q", "-f", CONSULTAS, "-g", goal, "-t", "halt"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
    except FileNotFoundError as e:
        raise PrologError("swipl no encontrado.") from e
    except subprocess.TimeoutExpired as e:
        raise PrologError("Prolog tardo demasiado.") from e
    if result.returncode != 0:
        error = result.stderr.strip().splitlines()
        raise PrologError(error[-1] if error else f"Prolog termino con codigo {result.returncode}")
    return result.stdout


def _parsear(linea):
    partes = linea.strip().split("|")
    if len(partes) == 5:
        return {
            "codigo": partes[0],
            "precio": int(partes[1]),
            "categoria": partes[2],
            "uso": partes[3],
            "stock": int(partes[4]),
        }
    return None


def _lista(goal):
    salida = _ejecutar(goal)
    return [p for p in (_parsear(l) for l in salida.splitlines()) if p]


def _args_cliente(cliente):
    return ",".join([
        atomo(cliente.nombre),
        entero(cliente.presupuesto),
        atomo(cliente.categoria),
        atomo(cliente.uso),
        atomo(cliente.marca),
    ])


def recomendar(cliente):
    return _lista(f"recomendar_cliente({_args_cliente(cliente)})")


def alternativas(cliente):
    return _lista(f"alternativas_cliente({_args_cliente(cliente)})")


def catalogo_categoria(categoria):
    return _lista(f"catalogo_categoria({atomo(categoria)})")


def verificar_stock(codigo):
    linea = _ejecutar(f"verificar_stock({atomo(codigo)})").strip()
    if linea.startswith("disponible"):
        return {"disponible": True, "stock": int(linea.split("|")[1])}
    return {"disponible": False, "stock": 0}


def extras():
    resultado = []
    for l in _ejecutar("extras").splitlines():
        partes = l.strip().split("|")
        if len(partes) == 4:
            resultado.append({
                "codigo": partes[0],
                "precio": int(partes[1]),
                "categoria": partes[2],
                "stock": int(partes[3]),
            })
    return resultado
