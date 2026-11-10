"""Une Prolog (que decide QUE recomendar) con Scala (que sabe COMO es cada producto)."""
from integracion import prolog_service, scala_service


def nombre(codigo):
    p = scala_service.producto(codigo)
    return p["nombre"] if p else codigo


def enriquecer(productos):
    """Completa los resultados de Prolog con nombre, marca y uso del catalogo Scala."""
    resultado = []
    for p in productos:
        info = scala_service.producto(p["codigo"]) or {}
        resultado.append({**info, **p,
                          "nombre": info.get("nombre", p["codigo"]),
                          "marca": info.get("marca", ""),
                          "uso": p.get("uso") or info.get("uso", "")})
    return resultado


def buscar_recomendaciones(cliente):
    """Devuelve (productos, es_alternativa). Si no hay coincidencias exactas,
    Prolog busca alternativas hasta 20% sobre el presupuesto."""
    productos = prolog_service.recomendar(cliente)
    es_alternativa = False
    if not productos:
        productos = prolog_service.alternativas(cliente)
        es_alternativa = True
    return enriquecer(productos), es_alternativa


def extras():
    return enriquecer(prolog_service.extras())


def marcas_de(categoria):
    """Marcas disponibles en una categoria: [(valor_prolog, etiqueta)]."""
    vistas = {}
    for p in scala_service.catalogo(categoria):
        vistas.setdefault(p["marca"].lower(), p["marca"])
    return sorted(vistas.items(), key=lambda x: x[1])


def mostrar_productos(lista):
    if not lista:
        print("  Sin resultados.")
        return
    print(f"\n  {'#':>3}  {'Codigo':<22} {'Nombre':<32} {'Precio':>8}  {'Uso':<8}  Stock")
    print("  " + "-" * 85)
    for i, p in enumerate(lista, 1):
        print(f"  {i:>3}  {p['codigo']:<22} {p['nombre']:<32} S/{p['precio']:>6}  {p.get('uso', ''):<8}  {p['stock']}")
