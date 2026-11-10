"""Interpretacion de texto libre en espanol: categorias, usos, presupuestos, marcas."""
import re
import unicodedata

CATEGORIAS = ["laptop", "celular", "tablet", "auricular", "accesorio", "monitor", "almacenamiento"]
USOS = ["estudio", "trabajo", "gaming"]

ETIQUETA_CATEGORIA = {
    "laptop": "Laptops", "celular": "Celulares", "tablet": "Tablets", "auricular": "Auriculares",
    "accesorio": "Accesorios", "monitor": "Monitores", "almacenamiento": "Almacenamiento",
}
ETIQUETA_USO = {"estudio": "Estudio", "trabajo": "Trabajo", "gaming": "Gaming"}

_SINONIMOS_CATEGORIA = {
    "laptop": ["laptop", "portatil", "notebook", "computadora", "computador", "pc", "lap"],
    "celular": ["celular", "telefono", "movil", "smartphone", "iphone", "cel"],
    "tablet": ["tablet", "tableta", "ipad"],
    "auricular": ["auricular", "audifono", "headphone", "headset", "airpods", "buds", "casco"],
    "accesorio": ["accesorio", "reloj", "smartwatch", "watch", "mouse", "raton", "teclado", "band", "pulsera"],
    "monitor": ["monitor", "pantalla"],
    "almacenamiento": ["almacenamiento", "disco", "ssd", "usb", "memoria", "pendrive", "externo"],
}
_SINONIMOS_USO = {
    "estudio": ["estudio", "estudiar", "estudiante", "universidad", "colegio", "clases", "escuela", "tareas"],
    "trabajo": ["trabajo", "trabajar", "oficina", "empresa", "negocio", "profesional", "chamba"],
    "gaming": ["gaming", "gamer", "juego", "jugar", "videojuego", "gamear"],
}
_SIN_MARCA = ["ninguna", "ninguno", "no", "sin preferencia", "cualquiera", "da igual", "me da igual",
              "no tengo", "indiferente", "sin marca", "nop"]

SI = ["si", "s", "claro", "dale", "ok", "okay", "confirmar", "confirmo", "confirma", "de acuerdo", "va", "listo"]
NO = ["no", "n", "cancelar", "cancela", "mejor no", "todavia no", "aun no"]


def normalizar(texto):
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", texto).strip()


def _palabras(texto):
    return re.findall(r"[a-z0-9]+", normalizar(texto))


def _coincide(texto, sinonimos):
    """True si alguna palabra del texto empieza por algun sinonimo (cubre plurales)."""
    palabras = _palabras(texto)
    for s in sinonimos:
        if " " in s:
            if s in normalizar(texto):
                return True
        elif any(p == s or (len(s) > 3 and p.startswith(s)) for p in palabras):
            return True
    return False


def detectar_categoria(texto):
    for cat, sinonimos in _SINONIMOS_CATEGORIA.items():
        if _coincide(texto, sinonimos):
            return cat
    return None


def detectar_uso(texto):
    for uso, sinonimos in _SINONIMOS_USO.items():
        if _coincide(texto, sinonimos):
            return uso
    return None


def es_sin_marca(texto):
    t = normalizar(texto)
    return t in _SIN_MARCA or any(t.startswith(x + " ") for x in _SIN_MARCA if " " in x)


def detectar_marca(texto, marcas_conocidas):
    """marcas_conocidas: iterable de marcas en minusculas (las del catalogo)."""
    palabras = set(_palabras(texto))
    for m in marcas_conocidas:
        if m in palabras:
            return m
    return None


def detectar_monto(texto):
    """Extrae un monto en soles: '2000', 'S/ 2,500', '3k', '1.5 mil', 'unos 1800 soles'."""
    t = normalizar(texto).replace("s/", " ").replace("s/.", " ")
    m = re.search(r"(\d+(?:[.,]\d+)*)\s*(k|mil)?\b", t)
    if not m:
        return None
    numero, sufijo = m.group(1), m.group(2)
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", numero):
        valor = float(re.sub(r"[.,]", "", numero))
    else:
        valor = float(numero.replace(",", "."))
    if sufijo:
        valor *= 1000
    return int(valor) if valor >= 1 else None


def detectar_entero(texto):
    m = re.search(r"\d+", str(texto))
    return int(m.group()) if m else None


def es_si(texto):
    return normalizar(texto) in SI


def es_no(texto):
    return normalizar(texto) in NO


def contiene(texto, *claves):
    return _coincide(texto, list(claves))
