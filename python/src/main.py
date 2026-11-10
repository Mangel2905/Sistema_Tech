import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from modelos.cliente import Cliente
from modelos.carrito import Carrito, IGV_PORCENTAJE
from integracion.prolog_service import PrologError
from integracion.scala_service import ScalaError, listar_todo, listar_categoria, reporte
from integracion.integrador import buscar_recomendaciones, mostrar_productos, extras

# carrito de la sesion de consola
carrito = Carrito()

# ── helpers de entrada ──────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")

def pedir_opcion(pregunta, validas):
    while True:
        resp = input(pregunta).strip().lower()
        if resp in validas:
            return resp
        print(f"  Escribe una de estas: {' / '.join(validas)}")

def pedir_entero(pregunta, minimo=1, maximo=99999):
    while True:
        resp = input(pregunta).strip()
        if resp.isdigit() and minimo <= int(resp) <= maximo:
            return int(resp)
        print(f"  Ingresa un numero entre {minimo} y {maximo}.")

def pedir_texto(pregunta):
    while True:
        resp = input(pregunta).strip()
        if resp:
            return resp
        print("  No puede estar vacio.")

def separador():
    print("  " + "─" * 60)

def header(cliente):
    print(f"\n  ══ TECHPOS │ {cliente.nombre} │ S/{cliente.presupuesto} ══")

# ── categorias y usos validos ───────────────

CATEGORIAS = ["laptop", "celular", "tablet", "auricular", "accesorio", "monitor", "almacenamiento"]
USOS = ["estudio", "trabajo", "gaming"]

# ── catalogo desde Scala ────────────────────

def mostrar_catalogo_categoria(cat):
    print(f"\n  ── {cat.upper()} ──")
    salida = listar_categoria(cat)
    if not salida.strip():
        print("  Sin productos disponibles.")
        return
    for l in salida.strip().splitlines():
        # solo filas de datos, no mensajes de sbt
        if l.strip() and l.strip()[0].isdigit():
            print(l)

def mostrar_catalogo_completo():
    print("\n  ╔══════════════════════════════════════════════╗")
    print("  ║         CATALOGO TECHPOS - 42 PRODUCTOS      ║")
    print("  ╚══════════════════════════════════════════════╝")
    salida = listar_todo()
    for l in salida.strip().splitlines():
        if l.strip() and not l.startswith("["):
            print(l)

# ── carrito ─────────────────────────────────

def agregar_al_carrito(productos, cliente):
    if not productos:
        print("  No hay productos para agregar.")
        return

    resp = pedir_opcion("\n  ¿Agregar al carrito? (s/n): ", ["s", "n"])
    if resp == "n":
        return

    print()
    for i, p in enumerate(productos, 1):
        print(f"  {i}. {p['nombre']} - S/{p['precio']} (stock: {p['stock']})")

    num = pedir_entero("  Numero del producto (0 para cancelar): ", 0, len(productos))
    if num == 0:
        return

    p = productos[num - 1]
    disponible_real = carrito.disponible(p)

    if disponible_real <= 0:
        print(f"  Ya tienes todo el stock en el carrito ({p['stock']} unidades).")
        return

    while True:
        cant = pedir_entero(f"  Cantidad (max {disponible_real}): ", 1, 9999)
        if cant <= disponible_real:
            break
        print(f"  No hay stock suficiente. Maximo: {disponible_real}.")

    carrito.agregar(p, cant)
    print(f"  ✓ Agregado: {p['nombre']} x{cant}")

    restante = carrito.restante(cliente.presupuesto)
    if restante < 0:
        print(f"  ⚠ El total (con IGV) supera tu presupuesto en S/{-restante}.")

def ver_carrito(cliente):
    if not carrito:
        print("\n  El carrito esta vacio.")
        return

    print("\n  ╔══════════════════════════════════════════════╗")
    print("  ║                   CARRITO                    ║")
    print("  ╚══════════════════════════════════════════════╝")
    print(f"  {'#':<4} {'Producto':<30} {'P.Unit':>7}  {'Cant':>4}  {'Subtotal':>9}")
    separador()

    r = carrito.resumen(cliente.presupuesto)
    for i, item in enumerate(r['items'], 1):
        print(f"  {i:<4} {item['nombre']:<30} S/{item['precio']:>5}  {item['cantidad']:>4}  S/{item['subtotal']:>7}")

    separador()
    print(f"  {'Subtotal:':<40} S/{r['subtotal']:>7}")
    print(f"  {f'IGV ({IGV_PORCENTAJE}%):':<40} S/{r['igv']:>7}")
    print(f"  {'TOTAL:':<40} S/{r['total']:>7}")
    print(f"  {'Presupuesto:':<40} S/{r['presupuesto']:>7}")
    if r['restante'] >= 0:
        print(f"  {'Restante:':<40} S/{r['restante']:>7}")
    else:
        print(f"  {'Excede en:':<40} S/{-r['restante']:>7}")

def eliminar_del_carrito():
    if not carrito:
        print("\n  El carrito esta vacio.")
        return

    print()
    for i, item in enumerate(carrito, 1):
        print(f"  {i}. {item['nombre']} x{item['cantidad']} - S/{item['precio'] * item['cantidad']}")

    num = pedir_entero("  Numero a eliminar (0 para cancelar): ", 0, len(carrito))
    if num == 0:
        return
    eliminado = carrito.eliminar_por_indice(num - 1)
    print(f"  ✓ Eliminado: {eliminado['nombre']}")

# ── registro inicial ─────────────────────────

def registrar_cliente():
    print("\n  ╔══════════════════════════════════════════════╗")
    print("  ║           BIENVENIDO A TECHPOS               ║")
    print("  ╚══════════════════════════════════════════════╝")
    print("  Cuéntanos sobre ti para personalizar tu experiencia.\n")

    nombre_c = pedir_texto("  Tu nombre: ")
    presupuesto = pedir_entero("  Presupuesto (S/): ", 1, 999999)

    print("\n  ¿Qué tipo de producto buscas?")
    for i, cat in enumerate(CATEGORIAS, 1):
        print(f"  {i}. {cat}")
    idx = pedir_entero("  Elige el numero: ", 1, len(CATEGORIAS))
    categoria = CATEGORIAS[idx - 1]

    uso = pedir_opcion("  ¿Para qué lo usarás? (estudio / trabajo / gaming): ", USOS)

    tiene_marca = pedir_opcion("  ¿Tienes marca preferida? (s/n): ", ["s", "n"])
    if tiene_marca == "s":
        marca = pedir_texto("  Marca: ").lower()
    else:
        marca = "ninguna"

    return Cliente(nombre_c, presupuesto, categoria, uso, marca)

# ── chatbot asesor ───────────────────────────

def chatbot(cliente):
    print("\n  ╔══════════════════════════════════════════════╗")
    print("  ║      ASESOR TECHPOS - Te ayudo a elegir      ║")
    print("  ╚══════════════════════════════════════════════╝")
    print("  (escribe 'cancelar' para salir)\n")

    uso = pedir_opcion("  ¿Para qué lo usarás? (estudio / trabajo / gaming): ", USOS + ["cancelar"])
    if uso == "cancelar":
        return

    print("\n  ¿Qué tipo de producto buscas?")
    for i, cat in enumerate(CATEGORIAS, 1):
        print(f"  {i}. {cat}")

    while True:
        idx_str = input("  Elige el numero (o 'cancelar'): ").strip().lower()
        if idx_str == "cancelar":
            return
        if idx_str.isdigit() and 1 <= int(idx_str) <= len(CATEGORIAS):
            categoria = CATEGORIAS[int(idx_str) - 1]
            break
        print(f"  Escribe un numero del 1 al {len(CATEGORIAS)}.")

    presupuesto = pedir_entero("  ¿Cuánto puedes gastar? S/: ", 1, 999999)

    tiene_marca = pedir_opcion("  ¿Tienes marca preferida? (s/n): ", ["s", "n"])
    marca = pedir_texto("  Marca: ").lower() if tiene_marca == "s" else "ninguna"

    cliente_tmp = Cliente(cliente.nombre, presupuesto, categoria, uso, marca)

    print("\n  Buscando recomendaciones...")
    productos, es_alt = buscar_recomendaciones(cliente_tmp)

    if not productos:
        print("  No encontramos productos con esas caracteristicas.")
        print("  Intenta con mayor presupuesto o sin marca preferida.")
    else:
        if es_alt:
            print("\n  No hay opciones exactas, pero estas estan cerca (hasta 20% mas):")
        else:
            print(f"\n  Encontramos {len(productos)} opcion(es) para ti:")
        mostrar_productos(productos)

        # accesorios complementarios
        ex = extras()
        if ex:
            print("\n  Accesorios que te pueden interesar:")
            mostrar_productos(ex[:3])

        agregar_al_carrito(productos, cliente)

    # buscar otro?
    if pedir_opcion("\n  ¿Buscar otro producto? (s/n): ", ["s", "n"]) == "s":
        chatbot(cliente)

# ── recomendaciones directas del perfil ─────

def ver_recomendaciones(cliente):
    print("\n  Buscando recomendaciones para tu perfil...")
    productos, es_alt = buscar_recomendaciones(cliente)

    if not productos:
        print("  No encontramos productos que coincidan con tu perfil.")
        print("  Usa el Asesor (opcion 4) para ajustar la busqueda.")
        return

    if es_alt:
        print("  No hay exactas, pero estas estan cerca (hasta 20% mas):")
    else:
        print(f"  {len(productos)} opcion(es) para tu perfil:")

    mostrar_productos(productos)
    agregar_al_carrito(productos, cliente)

# ── reportes desde Scala ─────────────────────

def ver_reportes():
    print("\n  Generando reportes...")
    salida = reporte()
    for l in salida.strip().splitlines():
        if not l.startswith("["):
            print(l)

def finalizar_compra(cliente):
    if not carrito:
        print("\n  El carrito esta vacio. Agrega productos antes de finalizar.")
        return

    print("\n  ╔══════════════════════════════════════════════╗")
    print("  ║             RESUMEN DE COMPRA                ║")
    print("  ╚══════════════════════════════════════════════╝")
    print(f"\n  Cliente:      {cliente.nombre}")
    print(f"  Presupuesto:  S/{cliente.presupuesto}")
    separador()

    r = carrito.resumen(cliente.presupuesto)
    for i, item in enumerate(r['items'], 1):
        print(f"  {i}. {item['nombre']:<30} x{item['cantidad']}  S/{item['subtotal']}")

    separador()
    print(f"  Subtotal:        S/{r['subtotal']}")
    print(f"  IGV ({IGV_PORCENTAJE}%):       S/{r['igv']}")
    print(f"  TOTAL A PAGAR:   S/{r['total']}")
    print(f"  Presupuesto:     S/{r['presupuesto']}")
    if r['restante'] >= 0:
        print(f"  Vuelto/Restante: S/{r['restante']}")
    else:
        print(f"  Excede en:       S/{-r['restante']}  ⚠")

    separador()
    confirmar = pedir_opcion("\n  ¿Confirmar compra? (s/n): ", ["s", "n"])
    if confirmar == "s":
        print("\n  ✓ ¡Compra realizada con exito!")
        print(f"  Gracias por tu compra, {cliente.nombre}. ¡Vuelve pronto!")
        carrito.clear()
    else:
        print("\n  Compra cancelada. Tu carrito sigue igual.")

# ── menu principal ───────────────────────────

def menu(cliente):
    while True:
        header(cliente)
        print("""
  1. Ver catalogo completo
  2. Ver catalogo por categoria
  3. Recomendaciones para mi
  4. Asesor - buscar producto
  5. Ver carrito
  6. Eliminar del carrito
  7. Reportes
  8. Finalizar compra
  9. Salir
""")
        op = pedir_opcion("  Opcion: ", ["1","2","3","4","5","6","7","8","9"])
        if op == "9":
            print("\n  ¡Hasta luego! Gracias por usar TechPOS.\n")
            break
        try:
            ejecutar_opcion(op, cliente)
        except (PrologError, ScalaError) as e:
            print(f"\n  [Error] {e}")


def ejecutar_opcion(op, cliente):
        if op == "1":
            mostrar_catalogo_completo()
        elif op == "2":
            print(f"\n  Categorias: {' / '.join(CATEGORIAS)}")
            cat = pedir_opcion("  Categoria: ", CATEGORIAS)
            mostrar_catalogo_categoria(cat)
        elif op == "3":
            ver_recomendaciones(cliente)
        elif op == "4":
            chatbot(cliente)
        elif op == "5":
            ver_carrito(cliente)
        elif op == "6":
            eliminar_del_carrito()
        elif op == "7":
            ver_reportes()
        elif op == "8":
            finalizar_compra(cliente)

# ── arranque ─────────────────────────────────

if __name__ == "__main__":
    print("""
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║         T E C H P O S                       ║
  ║      Sistema de Recomendacion Tech           ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝
""")
    cliente = registrar_cliente()
    print(f"\n  ¡Hola {cliente.nombre}! Tu presupuesto es S/{cliente.presupuesto}.")
    menu(cliente)