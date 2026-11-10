"""Motor conversacional de TechPOS.

Es independiente del framework web: recibe el texto o la accion del usuario y
devuelve una respuesta estructurada (mensajes + opciones rapidas) que cualquier
interfaz puede dibujar. FastAPI solo lo expone por HTTP.

Funciones (las mismas del menu de consola):
  registro del cliente, catalogo completo, catalogo por categoria,
  recomendaciones (Prolog), asesor, carrito (agregar / ver / eliminar),
  reportes (Scala) y finalizar compra.
"""
import threading
import time
import uuid
from dataclasses import dataclass, field

from chatbot import texto as tx
from integracion import integrador, inventario, scala_service
from integracion.inventario import CompraRechazada
from integracion.prolog_service import PrologError
from integracion.scala_service import ScalaError
from modelos.carrito import Carrito, StockInsuficiente
from modelos.cliente import Cliente

PASOS_REGISTRO = ["nombre", "presupuesto", "categoria", "uso", "marca"]
PASOS_ASESOR = ["uso", "categoria", "presupuesto", "marca"]
MAX_CHIPS_CANTIDAD = 5


def soles(monto):
    return f"S/ {monto:,}"


# ─────────────────────────── sesion ───────────────────────────

@dataclass
class Sesion:
    id: str
    cliente: Cliente = None
    carrito: Carrito = field(default_factory=Carrito)
    estado: str = "perfil"          # perfil | libre | cantidad | elegir_categoria | confirmar
    modo: str = "registro"          # registro | asesor  (solo en estado 'perfil')
    borrador: dict = field(default_factory=dict)
    pendiente: str = None           # codigo del producto que se esta agregando
    actualizada: float = field(default_factory=time.time)

    def paso_actual(self):
        pasos = PASOS_REGISTRO if self.modo == "registro" else PASOS_ASESOR
        return next((p for p in pasos if p not in self.borrador), None)


class AlmacenSesiones:
    """Sesiones en memoria. Suficiente para un proyecto academico/demo."""

    def __init__(self, ttl_segundos=4 * 3600):
        self._sesiones = {}
        self._lock = threading.Lock()
        self.ttl = ttl_segundos

    def crear(self):
        s = Sesion(id=uuid.uuid4().hex)
        with self._lock:
            self._limpiar()
            self._sesiones[s.id] = s
        return s

    def obtener(self, sesion_id):
        with self._lock:
            s = self._sesiones.get(sesion_id)
            if s:
                s.actualizada = time.time()
            return s

    def _limpiar(self):
        limite = time.time() - self.ttl
        for k in [k for k, s in self._sesiones.items() if s.actualizada < limite]:
            del self._sesiones[k]


# ─────────────────────────── respuesta ───────────────────────────

class Respuesta:
    def __init__(self):
        self.mensajes = []
        self.opciones = []
        self.entrada = {"tipo": "texto", "placeholder": "Escribe un mensaje…"}

    def texto(self, t):
        self.mensajes.append({"tipo": "texto", "texto": t})
        return self

    def aviso(self, t, nivel="info"):
        self.mensajes.append({"tipo": "aviso", "nivel": nivel, "texto": t})
        return self

    def productos(self, lista, titulo=None, agrupar=False, agregable=True):
        self.mensajes.append({"tipo": "productos", "titulo": titulo, "agrupar": agrupar,
                              "agregable": agregable, "productos": lista})
        return self

    def carrito(self, resumen, editable=True, titulo="Tu carrito"):
        self.mensajes.append({"tipo": "carrito", "titulo": titulo, "editable": editable, **resumen})
        return self

    def reporte(self, datos):
        self.mensajes.append({"tipo": "reporte", **datos})
        return self

    def opcion(self, etiqueta, accion, valor=None, estilo=None):
        self.opciones.append({"etiqueta": etiqueta, "accion": accion, "valor": valor, "estilo": estilo})
        return self

    def pedir(self, tipo="texto", placeholder="Escribe un mensaje…"):
        self.entrada = {"tipo": tipo, "placeholder": placeholder}
        return self


# ─────────────────────────── motor ───────────────────────────

ACCIONES_MENU = {"menu", "recomendaciones", "asesor", "catalogo", "elegir_categoria",
                 "catalogo_categoria", "carrito", "reportes", "finalizar", "agregar", "eliminar"}


class Motor:

    # ── entrada principal ──
    def bienvenida(self, s):
        r = Respuesta()
        r.texto("¡Hola! Soy el asesor de **TechPOS**. Te ayudo a encontrar tecnología "
                "que se ajuste a lo que necesitas y a tu presupuesto.")
        r.texto("Para empezar, ¿cómo te llamas?")
        r.pedir("texto", "Tu nombre")
        return self._empaquetar(s, r)

    def procesar(self, s, texto=None, accion=None, valor=None):
        r = Respuesta()
        texto = (texto or "").strip()
        try:
            self._despachar(s, r, texto, accion, valor)
        except PrologError as e:
            r.aviso(f"El motor de recomendaciones (Prolog) no respondió: {e}", "error")
            self._menu(s, r)
        except ScalaError as e:
            r.aviso(f"El catálogo (Scala) no respondió: {e}", "error")
            self._menu(s, r)
        return self._empaquetar(s, r)

    def _despachar(self, s, r, texto, accion, valor):
        # Mientras no hay cliente registrado, solo se avanza en el registro.
        if s.cliente is None:
            return self._paso_perfil(s, r, texto, valor)

        # Un boton de menu siempre interrumpe el flujo en curso.
        if accion in ACCIONES_MENU:
            s.estado, s.pendiente = "libre", None
            return self._accion(s, r, accion, valor)

        if accion == "cancelar":
            s.estado, s.pendiente = "libre", None
            r.texto("Listo, cancelado. ¿Qué más quieres hacer?")
            return self._menu(s, r)

        if s.estado == "perfil":
            return self._paso_perfil(s, r, texto, valor)
        if s.estado == "cantidad":
            return self._paso_cantidad(s, r, texto, valor)
        if s.estado == "elegir_categoria":
            cat = valor if valor in tx.CATEGORIAS else tx.detectar_categoria(texto)
            if cat:
                s.estado = "libre"
                return self._catalogo_categoria(s, r, cat)
            r.texto("No reconocí esa categoría. Elige una de estas:")
            return self._chips_categorias(r, "catalogo_categoria")
        if s.estado == "confirmar":
            return self._paso_confirmar(s, r, texto, accion)

        return self._texto_libre(s, r, texto)

    # ── acciones de menu ──
    def _accion(self, s, r, accion, valor):
        if accion == "menu":
            r.texto("¿Qué quieres hacer?")
            return self._menu(s, r)
        if accion == "recomendaciones":
            return self._recomendaciones(s, r, s.cliente, titulo="Recomendado para tu perfil")
        if accion == "asesor":
            return self._iniciar_asesor(s, r)
        if accion == "catalogo":
            return self._catalogo(s, r)
        if accion == "elegir_categoria":
            s.estado = "elegir_categoria"
            r.texto("¿Qué categoría quieres ver?")
            return self._chips_categorias(r, "catalogo_categoria")
        if accion == "catalogo_categoria":
            return self._catalogo_categoria(s, r, valor)
        if accion == "carrito":
            return self._ver_carrito(s, r)
        if accion == "reportes":
            return self._reportes(s, r)
        if accion == "finalizar":
            return self._finalizar(s, r)
        if accion == "agregar":
            return self._iniciar_agregar(s, r, valor)
        if accion == "eliminar":
            return self._eliminar(s, r, valor)

    def _menu(self, s, r, extra=True):
        n = sum(i["cantidad"] for i in s.carrito)
        r.opcion("Recomendaciones para mí", "recomendaciones")
        r.opcion("Buscar otro producto", "asesor")
        r.opcion("Catálogo completo", "catalogo")
        r.opcion("Ver por categoría", "elegir_categoria")
        r.opcion(f"Carrito ({n})" if n else "Carrito", "carrito")
        r.opcion("Reportes", "reportes")
        if n and extra:
            r.opcion("Finalizar compra", "finalizar", estilo="primario")
        r.pedir("texto", "Escribe, por ejemplo: «busco una laptop para gaming de 3000»")

    # ── registro / asesor (mismo flujo de preguntas) ──
    def _iniciar_asesor(self, s, r, prellenado=None):
        s.estado, s.modo = "perfil", "asesor"
        s.borrador = dict(prellenado or {})
        if not prellenado:
            r.texto("Perfecto, busquemos algo nuevo. Puedes cancelar cuando quieras.")
        return self._preguntar(s, r) if s.paso_actual() else self._completar_perfil(s, r)

    def _preguntar(self, s, r):
        paso = s.paso_actual()
        nombre = s.cliente.nombre if s.cliente else s.borrador.get("nombre", "")
        if paso == "nombre":
            r.texto("¿Cómo te llamas?")
            r.pedir("texto", "Tu nombre")
        elif paso == "presupuesto":
            r.texto(f"Mucho gusto, {nombre}. ¿Cuál es tu presupuesto en soles?"
                    if s.modo == "registro" else "¿Cuánto puedes gastar?")
            for monto in (500, 1000, 2000, 3000):
                r.opcion(soles(monto), "responder", monto)
            r.pedir("numero", "Monto en soles, ej. 1800")
        elif paso == "categoria":
            r.texto("¿Qué tipo de producto buscas?")
            self._chips_categorias(r, "responder")
            r.pedir("texto", "Ej. laptop, celular, audífonos…")
        elif paso == "uso":
            r.texto("¿Para qué lo vas a usar principalmente?")
            for uso in tx.USOS:
                r.opcion(tx.ETIQUETA_USO[uso], "responder", uso)
            r.pedir("texto", "Estudio, trabajo o gaming")
        elif paso == "marca":
            r.texto("¿Tienes alguna marca preferida?")
            r.opcion("Sin preferencia", "responder", "ninguna")
            for valor, etiqueta in integrador.marcas_de(s.borrador["categoria"]):
                r.opcion(etiqueta, "responder", valor)
            r.pedir("texto", "Escribe la marca o «ninguna»")
        if s.modo == "asesor":
            r.opcion("Cancelar", "cancelar", estilo="sutil")

    def _paso_perfil(self, s, r, texto, valor):
        paso = s.paso_actual()
        entrada = valor if valor is not None else texto
        error = None

        if paso == "nombre":
            nombre = " ".join(str(entrada).split())[:40]
            if nombre:
                s.borrador["nombre"] = nombre
            else:
                error = "Necesito tu nombre para continuar."
        elif paso == "presupuesto":
            monto = entrada if isinstance(entrada, int) else tx.detectar_monto(entrada)
            if monto and 1 <= monto <= 999999:
                s.borrador["presupuesto"] = monto
            else:
                error = "No entendí el monto. Escribe solo el número, por ejemplo 1500."
        elif paso == "categoria":
            cat = entrada if entrada in tx.CATEGORIAS else tx.detectar_categoria(entrada)
            if cat:
                s.borrador["categoria"] = cat
            else:
                error = "No reconocí esa categoría."
        elif paso == "uso":
            uso = entrada if entrada in tx.USOS else tx.detectar_uso(entrada)
            if uso:
                s.borrador["uso"] = uso
            else:
                error = "Elige estudio, trabajo o gaming."
        elif paso == "marca":
            if valor is not None:
                s.borrador["marca"] = valor
            elif tx.es_sin_marca(texto):
                s.borrador["marca"] = "ninguna"
            elif texto:
                s.borrador["marca"] = tx.normalizar(texto)
            else:
                error = "Escribe una marca o elige «Sin preferencia»."

        if error:
            r.aviso(error, "advertencia")
            return self._preguntar(s, r)
        if s.paso_actual():
            return self._preguntar(s, r)
        return self._completar_perfil(s, r)

    def _completar_perfil(self, s, r):
        b = s.borrador
        if s.modo == "registro":
            s.cliente = Cliente(b["nombre"], b["presupuesto"], b["categoria"], b["uso"], b["marca"])
            s.estado, s.borrador = "libre", {}
            r.texto(f"¡Listo, {s.cliente.nombre}! Busqué en el catálogo según tu perfil.")
            return self._recomendaciones(s, r, s.cliente, titulo="Recomendado para ti")
        # asesor: busqueda temporal, sin cambiar el perfil del cliente
        temporal = Cliente(s.cliente.nombre, b["presupuesto"], b["categoria"], b["uso"], b["marca"])
        s.estado, s.borrador = "libre", {}
        return self._recomendaciones(s, r, temporal, titulo="Resultados de tu búsqueda", con_extras=True)

    # ── recomendaciones (Prolog) ──
    def _recomendaciones(self, s, r, cliente, titulo, con_extras=False):
        productos, es_alt = integrador.buscar_recomendaciones(cliente)
        detalle = (f"{tx.ETIQUETA_CATEGORIA[cliente.categoria].lower()} para {cliente.uso}, "
                   f"hasta {soles(cliente.presupuesto)}"
                   + ("" if cliente.marca == "ninguna" else f", marca {cliente.marca}"))
        if not productos:
            r.texto(f"No encontré {detalle}. Prueba con un presupuesto mayor o sin marca preferida.")
            r.opcion("Ajustar búsqueda", "asesor", estilo="primario")
            return self._menu(s, r)
        if es_alt:
            r.texto(f"No hay coincidencias exactas para {detalle}, "
                    "pero estas opciones están cerca (hasta 20% más):")
        else:
            r.texto(f"Encontré {len(productos)} {'opción' if len(productos) == 1 else 'opciones'} "
                    f"de {detalle}:")
        r.productos(self._con_disponible(s, productos), titulo=titulo)
        if con_extras:
            ex = integrador.extras()[:3]
            if ex:
                r.productos(self._con_disponible(s, ex), titulo="Accesorios que te pueden interesar")
        return self._menu(s, r)

    # ── catalogo (Scala) ──
    def _catalogo(self, s, r):
        productos = scala_service.catalogo()
        r.texto(f"Este es el catálogo completo: {len(productos)} productos.")
        r.productos(self._con_disponible(s, productos), titulo="Catálogo TechPOS", agrupar=True)
        return self._menu(s, r)

    def _catalogo_categoria(self, s, r, categoria):
        if categoria not in tx.CATEGORIAS:
            r.aviso("Categoría no válida.", "advertencia")
            return self._chips_categorias(r, "catalogo_categoria")
        productos = scala_service.catalogo(categoria)
        etiqueta = tx.ETIQUETA_CATEGORIA[categoria]
        if not productos:
            r.texto(f"No hay {etiqueta.lower()} con stock en este momento.")
        else:
            r.productos(self._con_disponible(s, productos), titulo=etiqueta)
        return self._menu(s, r)

    def _chips_categorias(self, r, accion):
        for cat in tx.CATEGORIAS:
            r.opcion(tx.ETIQUETA_CATEGORIA[cat], accion, cat)
        return r

    # ── carrito ──
    def _con_disponible(self, s, productos):
        return [dict(p, disponible=s.carrito.disponible(p)) for p in productos]

    def _iniciar_agregar(self, s, r, codigo):
        p = scala_service.producto(codigo)
        if not p:
            r.aviso("No encontré ese producto.", "advertencia")
            return self._menu(s, r)
        if p["stock"] <= 0:
            r.aviso(f"{p['nombre']} está agotado. No se puede agregar al carrito.", "advertencia")
            return self._menu(s, r)
        disp = s.carrito.disponible(p)
        if disp <= 0:
            r.aviso(f"Ya tienes en el carrito todo el stock de {p['nombre']} ({p['stock']} u.).",
                    "advertencia")
            return self._menu(s, r)
        if disp == 1:
            return self._agregar(s, r, p, 1)
        s.estado, s.pendiente = "cantidad", codigo
        r.texto(f"¿Cuántas unidades de **{p['nombre']}** quieres? (máximo {disp})")
        for n in range(1, min(disp, MAX_CHIPS_CANTIDAD) + 1):
            r.opcion(str(n), "cantidad", n)
        r.opcion("Cancelar", "cancelar", estilo="sutil")
        r.pedir("numero", f"Cantidad (1 a {disp})")

    def _paso_cantidad(self, s, r, texto, valor):
        p = scala_service.producto(s.pendiente)
        cant = valor if isinstance(valor, int) else tx.detectar_entero(texto)
        disp = s.carrito.disponible(p)
        if disp <= 0:   # se agoto mientras el cliente elegia la cantidad
            s.estado, s.pendiente = "libre", None
            r.aviso(f"{p['nombre']} ya no tiene stock disponible.", "advertencia")
            return self._menu(s, r)
        if cant is None or not 1 <= cant <= disp:
            r.aviso(f"Indica una cantidad entre 1 y {disp}.", "advertencia")
            for n in range(1, min(disp, MAX_CHIPS_CANTIDAD) + 1):
                r.opcion(str(n), "cantidad", n)
            r.opcion("Cancelar", "cancelar", estilo="sutil")
            return r.pedir("numero", f"Cantidad (1 a {disp})")
        return self._agregar(s, r, p, cant)

    def _agregar(self, s, r, p, cantidad):
        s.estado, s.pendiente = "libre", None
        try:
            s.carrito.agregar(p, cantidad)
        except StockInsuficiente as e:
            r.aviso(str(e), "advertencia")
            return self._menu(s, r)
        r.aviso(f"Agregado: {p['nombre']} × {cantidad}", "exito")
        restante = s.carrito.restante(s.cliente.presupuesto)
        if restante < 0:
            r.aviso(f"El total con IGV supera tu presupuesto por {soles(-restante)}.", "advertencia")
        r.opcion("Ver carrito", "carrito")
        r.opcion("Finalizar compra", "finalizar", estilo="primario")
        r.opcion("Seguir buscando", "menu")
        r.pedir("texto", "¿Algo más?")

    def _sincronizar(self, s, r):
        """Ajusta el carrito si el stock bajo (por ejemplo, otro cliente compro)."""
        for c in s.carrito.sincronizar(inventario.stock_actual()):
            if c["ahora"] == 0:
                r.aviso(f"{c['nombre']} se agotó y lo quité de tu carrito.", "advertencia")
            else:
                r.aviso(f"Solo quedan {c['ahora']} unidades de {c['nombre']}; "
                        f"ajusté tu carrito (tenías {c['antes']}).", "advertencia")

    def _ver_carrito(self, s, r):
        self._sincronizar(s, r)
        if s.carrito.vacio():
            r.texto("Tu carrito está vacío. Mira tus recomendaciones o el catálogo para agregar productos.")
            return self._menu(s, r)
        r.carrito(s.carrito.resumen(s.cliente.presupuesto))
        return self._menu(s, r)

    def _eliminar(self, s, r, codigo):
        item = s.carrito.eliminar(codigo)
        if item:
            r.aviso(f"Eliminado: {item['nombre']}", "info")
        return self._ver_carrito(s, r)

    # ── reportes (Scala) ──
    def _reportes(self, s, r):
        datos = scala_service.reportes()
        r.texto("Estos son los reportes del inventario, generados por el módulo Scala:")
        r.reporte({
            "stock_bajo": datos["stockBajo"],
            "agotados": datos.get("agotados", []),
            "resumen": [dict(x, etiqueta=tx.ETIQUETA_CATEGORIA.get(x["categoria"], x["categoria"]))
                        for x in datos["resumen"]],
        })
        return self._menu(s, r)

    # ── compra ──
    def _finalizar(self, s, r):
        if not s.carrito.vacio():
            scala_service.invalidar_cache()   # stock fresco (pudo comprarse desde otra app)
            self._sincronizar(s, r)
        if s.carrito.vacio():
            r.texto("Tu carrito está vacío. Agrega productos antes de finalizar.")
            return self._menu(s, r)
        s.estado = "confirmar"
        resumen = s.carrito.resumen(s.cliente.presupuesto)
        r.carrito(resumen, editable=False, titulo="Resumen de compra")
        if resumen["restante"] < 0:
            r.aviso(f"Ojo: el total supera tu presupuesto por {soles(-resumen['restante'])}.", "advertencia")
        r.texto("¿Confirmas la compra?")
        r.opcion("Confirmar compra", "confirmar", estilo="primario")
        r.opcion("Seguir comprando", "cancelar", estilo="sutil")
        r.pedir("texto", "Sí / No")

    def _paso_confirmar(self, s, r, texto, accion):
        if accion == "confirmar" or tx.es_si(texto):
            total = s.carrito.total()
            try:
                inventario.registrar_compra(list(s.carrito))   # descuenta el stock (todo o nada)
            except CompraRechazada:
                r.aviso("El stock cambió mientras comprabas, así que no se cobró nada. "
                        "Revisa el resumen actualizado.", "advertencia")
                return self._finalizar(s, r)
            s.carrito.vaciar()
            s.estado = "libre"
            r.aviso(f"¡Compra realizada con éxito! Total pagado: {soles(total)}", "exito")
            r.texto(f"Gracias por tu compra, {s.cliente.nombre}. ¿Te ayudo con algo más?")
            return self._menu(s, r)
        if tx.es_no(texto):
            s.estado = "libre"
            r.texto("Compra cancelada. Tu carrito sigue igual.")
            return self._menu(s, r)
        r.texto("¿Confirmas la compra? Responde sí o no.")
        r.opcion("Confirmar compra", "confirmar", estilo="primario")
        r.opcion("Seguir comprando", "cancelar", estilo="sutil")

    # ── texto libre (estado 'libre') ──
    def _texto_libre(self, s, r, texto):
        if not texto:
            r.texto("¿Qué quieres hacer?")
            return self._menu(s, r)

        categoria = tx.detectar_categoria(texto)
        uso = tx.detectar_uso(texto)
        monto = tx.detectar_monto(texto)
        monto = monto if monto and monto >= 50 else None
        marcas = {p["marca"].lower() for p in scala_service.catalogo()}
        marca = tx.detectar_marca(texto, marcas)
        busca = tx.contiene(texto, "busco", "buscar", "quiero", "necesito", "recomienda",
                            "recomiendame", "comprar", "dame", "muestrame", "tienes", "hay")

        # "busco una laptop para gaming de 3000" -> asesor con los datos ya llenos
        if categoria and (uso or monto or marca or busca):
            pre = {"categoria": categoria}
            if uso:
                pre["uso"] = uso
            if monto:
                pre["presupuesto"] = monto
            if marca:
                pre["marca"] = marca
            faltan = [p for p in PASOS_ASESOR if p not in pre]
            if faltan:
                r.texto(f"Entendido: buscas {tx.ETIQUETA_CATEGORIA[categoria].lower()}. "
                        "Solo me faltan un par de datos.")
            return self._iniciar_asesor(s, r, prellenado=pre)
        if categoria:
            return self._catalogo_categoria(s, r, categoria)

        if tx.contiene(texto, "carrito", "eliminar", "quitar", "borrar"):
            return self._ver_carrito(s, r)
        if tx.contiene(texto, "pagar", "finalizar", "terminar", "checkout", "comprar"):
            return self._finalizar(s, r)
        if tx.contiene(texto, "recomendacion", "recomienda", "recomendado", "para mi", "perfil"):
            return self._recomendaciones(s, r, s.cliente, titulo="Recomendado para tu perfil")
        if tx.contiene(texto, "catalogo", "productos", "todo", "lista"):
            return self._catalogo(s, r)
        if tx.contiene(texto, "reporte", "stock", "inventario", "estadistica", "resumen"):
            return self._reportes(s, r)
        if tx.contiene(texto, "categoria", "categorias"):
            return self._accion(s, r, "elegir_categoria", None)
        if tx.contiene(texto, "buscar", "asesor", "otro", "busco", "ayudame"):
            return self._iniciar_asesor(s, r)
        if tx.contiene(texto, "gracias"):
            r.texto("¡De nada! ¿Te ayudo con algo más?")
            return self._menu(s, r)
        if tx.contiene(texto, "hola", "buenas", "menu", "ayuda", "opciones", "inicio"):
            r.texto(f"Hola, {s.cliente.nombre}. Esto es lo que puedo hacer por ti:")
            return self._menu(s, r)

        r.texto("No estoy seguro de haberte entendido. Puedes escribirme algo como "
                "«busco un celular para trabajo de 2500» o elegir una opción:")
        return self._menu(s, r)

    # ── salida ──
    def _empaquetar(self, s, r):
        c = s.cliente
        return {
            "sesion_id": s.id,
            "mensajes": r.mensajes,
            "opciones": r.opciones,
            "entrada": r.entrada,
            "perfil": None if c is None else {
                "nombre": c.nombre, "presupuesto": c.presupuesto, "categoria": c.categoria,
                "uso": c.uso, "marca": c.marca,
            },
            "carrito": {"unidades": sum(i["cantidad"] for i in s.carrito),
                        "total": s.carrito.total()},
        }
