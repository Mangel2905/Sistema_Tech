import subprocess
import os
import shutil

SCALA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../scala"))
JAR_PATH = os.path.join(SCALA_DIR, "target", "out", "jvm", "scala-2.13.12", "sistema-tech", "Sistema-Tech-assembly-0.1.0.jar")

def _ejecutar(args):
    if not os.path.exists(JAR_PATH):
        print("  [Error] JAR no encontrado. Corre 'sbt assembly' en la carpeta scala.")
        return ""
    try:
        result = subprocess.run(
            ["java", "-jar", JAR_PATH] + args,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=SCALA_DIR
        )
        return result.stdout
    except FileNotFoundError:
        print("  [Error] Java no encontrado en el PATH.")
        return ""
    except subprocess.TimeoutExpired:
        print("  [Error] Scala tardo demasiado.")
        return ""

def listar_todo():
    return _ejecutar(["listar"])

def listar_categoria(categoria):
    return _ejecutar(["listar", categoria])

def reporte():
    return _ejecutar(["reporte"])