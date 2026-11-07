import subprocess
import os
import shutil

BASE = os.path.dirname(__file__)
CONSULTAS = os.path.abspath(os.path.join(BASE, "../../../prolog/consultas.pl"))

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

def _ejecutar(goal):
    swipl = _swipl_cmd()
    if swipl is None:
        print("  [Error] swipl no encontrado. Instala SWI-Prolog.")
        return ""
    try:
        result = subprocess.run(
            [swipl, "-q", "-f", CONSULTAS, "-g", goal, "-t", "halt"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    except FileNotFoundError:
        print("  [Error] swipl no encontrado.")
        return ""
    except subprocess.TimeoutExpired:
        print("  [Error] Prolog tardo demasiado.")
        return ""

def _parsear(linea):
    partes = linea.strip().split("|")
    if len(partes) == 5:
        return {
            "codigo": partes[0],
            "precio": int(partes[1]),
            "categoria": partes[2],
            "uso": partes[3],
            "stock": int(partes[4])
        }
    return None

def recomendar(cliente):
    goal = f"recomendar_cliente('{cliente.nombre}',{cliente.presupuesto},'{cliente.categoria}','{cliente.uso}','{cliente.marca}')"
    salida = _ejecutar(goal)
    return [p for p in (_parsear(l) for l in salida.splitlines()) if p]

def alternativas(cliente):
    goal = f"alternativas_cliente('{cliente.nombre}',{cliente.presupuesto},'{cliente.categoria}','{cliente.uso}','{cliente.marca}')"
    salida = _ejecutar(goal)
    return [p for p in (_parsear(l) for l in salida.splitlines()) if p]

def catalogo_categoria(categoria):
    goal = f"catalogo_categoria('{categoria}')"
    salida = _ejecutar(goal)
    return [p for p in (_parsear(l) for l in salida.splitlines()) if p]

def verificar_stock(codigo):
    goal = f"verificar_stock({codigo})"
    salida = _ejecutar(goal)
    linea = salida.strip()
    if linea.startswith("disponible"):
        partes = linea.split("|")
        return {"disponible": True, "stock": int(partes[1])}
    return {"disponible": False, "stock": 0}

def extras():
    salida = _ejecutar("extras")
    resultado = []
    for l in salida.splitlines():
        partes = l.strip().split("|")
        if len(partes) == 4:
            resultado.append({
                "codigo": partes[0],
                "precio": int(partes[1]),
                "categoria": partes[2],
                "stock": int(partes[3])
            })
    return resultado