"use strict";

/* TechPOS · cliente del chat.
   El backend (FastAPI) decide la conversación; aquí solo se dibujan los mensajes
   estructurados que devuelve: texto, aviso, productos, carrito y reporte. */

const $ = (sel) => document.querySelector(sel);
const hilo = $("#hilo");
const zona = $("#conversacion");
const form = $("#composer");
const entrada = $("#entrada");
const btnEnviar = $("#enviar");
const btnCarrito = $("#btn-carrito");
const badge = $("#badge");
const perfilEl = $("#perfil");

let sesionId = null;
let ocupado = false;
let chipsActuales = null;

const ETIQUETAS = {
  laptop: "Laptops", celular: "Celulares", tablet: "Tablets", auricular: "Auriculares",
  accesorio: "Accesorios", monitor: "Monitores", almacenamiento: "Almacenamiento",
};

/* ───────── utilidades ───────── */

const soles = (n) => "S/ " + Number(n).toLocaleString("es-PE");

function el(tag, props = {}, ...hijos) {
  const nodo = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") nodo.className = v;
    else if (k === "text") nodo.textContent = v;
    else if (k.startsWith("on")) nodo.addEventListener(k.slice(2), v);
    else nodo.setAttribute(k, v === true ? "" : v);
  }
  for (const h of hijos.flat()) if (h !== null && h !== undefined && h !== false) nodo.append(h);
  return nodo;
}

function icono(id) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("aria-hidden", "true");
  const use = document.createElementNS(ns, "use");
  use.setAttribute("href", "#i-" + id);
  svg.append(use);
  return svg;
}

/* **negrita** sin innerHTML (el texto nunca se interpreta como HTML) */
function textoRico(t) {
  const p = el("p");
  t.split(/(\*\*[^*]+\*\*)/g).forEach((parte) => {
    if (parte.startsWith("**") && parte.endsWith("**")) p.append(el("strong", { text: parte.slice(2, -2) }));
    else if (parte) p.append(parte);
  });
  return p;
}

function bajar(turno) {
  requestAnimationFrame(() => {
    if (turno && turno.offsetHeight > zona.clientHeight * 0.75) {
      turno.scrollIntoView({ block: "start", behavior: "smooth" });
    } else {
      zona.scrollTo({ top: zona.scrollHeight, behavior: "smooth" });
    }
  });
}

/* ───────── red ───────── */

async function api(ruta, cuerpo) {
  const r = await fetch(ruta, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: cuerpo ? JSON.stringify(cuerpo) : undefined,
  });
  if (!r.ok) {
    const err = new Error((await r.json().catch(() => ({}))).detail || `Error ${r.status}`);
    err.status = r.status;
    throw err;
  }
  return r.json();
}

async function iniciar() {
  hilo.replaceChildren();
  sesionId = null;
  actualizarEstado({ perfil: null, carrito: { unidades: 0 } });
  const escribiendo = mostrarEscribiendo();
  try {
    const resp = await api("/api/chat/sesion");
    escribiendo.remove();
    dibujarRespuesta(resp);
  } catch (e) {
    escribiendo.remove();
    dibujarError("No pude conectar con el servidor. ¿Está corriendo uvicorn?", iniciar);
  }
}

async function enviar({ texto = null, accion = null, valor = null, etiqueta = null }) {
  if (ocupado || !sesionId) return;
  const mostrado = etiqueta || texto;
  if (!mostrado) return;

  ocupado = true;
  quitarChips();
  hilo.append(el("div", { class: "turno turno-usuario" }, el("div", { class: "burbuja", text: mostrado })));
  const escribiendo = mostrarEscribiendo();
  bajar();

  try {
    const resp = await api("/api/chat", { sesion_id: sesionId, texto: texto ?? mostrado, accion, valor });
    escribiendo.remove();
    dibujarRespuesta(resp);
  } catch (e) {
    escribiendo.remove();
    if (e.status === 404) {
      dibujarError("Tu sesión expiró. Empecemos una nueva conversación.", iniciar, "Empezar de nuevo");
    } else {
      dibujarError(e.message || "Algo salió mal.", () => enviar({ texto, accion, valor, etiqueta }), "Reintentar");
    }
  } finally {
    ocupado = false;
    actualizarBoton();
    entrada.focus({ preventScroll: true });
  }
}

/* ───────── dibujo ───────── */

function turnoBot() {
  const contenido = el("div", { class: "contenido" });
  const turno = el("div", { class: "turno turno-bot" },
    el("div", { class: "avatar", "aria-hidden": "true" }, icono("chip")), contenido);
  hilo.append(turno);
  return { turno, contenido };
}

function mostrarEscribiendo() {
  const { turno, contenido } = turnoBot();
  contenido.append(el("div", { class: "escribiendo", "aria-label": "El asesor está escribiendo" },
    el("span"), el("span"), el("span")));
  return turno;
}

function dibujarRespuesta(resp) {
  sesionId = resp.sesion_id;
  const { turno, contenido } = turnoBot();
  for (const m of resp.mensajes) {
    const nodo = RENDER[m.tipo]?.(m);
    if (nodo) contenido.append(nodo);
  }
  if (resp.opciones?.length) {
    chipsActuales = el("div", { class: "chips", role: "group", "aria-label": "Respuestas sugeridas" },
      resp.opciones.map((o) => el("button", {
        type: "button",
        class: "chip" + (o.estilo ? " chip-" + o.estilo : ""),
        text: o.etiqueta,
        onclick: () => enviar({ accion: o.accion, valor: o.valor, etiqueta: o.etiqueta }),
      })));
    contenido.append(chipsActuales);
  }
  actualizarEstado(resp);
  bajar(turno);
}

function dibujarError(texto, reintentar, etiqueta = "Reintentar") {
  const { turno, contenido } = turnoBot();
  contenido.append(RENDER.aviso({ nivel: "error", texto }));
  chipsActuales = el("div", { class: "chips" },
    el("button", { type: "button", class: "chip chip-primario", text: etiqueta, onclick: () => { quitarChips(); reintentar(); } }));
  contenido.append(chipsActuales);
  bajar(turno);
}

function quitarChips() {
  if (chipsActuales) chipsActuales.remove();
  chipsActuales = null;
}

function actualizarEstado(resp) {
  const p = resp.perfil;
  if (p) {
    perfilEl.hidden = false;
    perfilEl.replaceChildren(el("strong", { text: p.nombre }), ` · ${soles(p.presupuesto)}`);
    perfilEl.title = `${ETIQUETAS[p.categoria] || p.categoria} · ${p.uso} · marca: ${p.marca}`;
  } else {
    perfilEl.hidden = true;
  }
  btnCarrito.disabled = !p;
  const n = resp.carrito?.unidades || 0;
  badge.hidden = n === 0;
  badge.textContent = n;
  btnCarrito.setAttribute("aria-label", n ? `Ver carrito (${n} productos)` : "Ver carrito");

  if (resp.entrada) {
    entrada.placeholder = resp.entrada.placeholder || "Escribe un mensaje…";
    entrada.inputMode = resp.entrada.tipo === "numero" ? "numeric" : "text";
  }
}

/* ───────── tipos de mensaje ───────── */

const RENDER = {
  texto: (m) => textoRico(m.texto),

  aviso: (m) => {
    const ic = { exito: "check", advertencia: "alert", error: "alert" }[m.nivel] || "info";
    return el("div", { class: `aviso aviso-${m.nivel || "info"}`, role: m.nivel === "error" ? "alert" : null },
      icono(ic), el("span", { text: m.texto }));
  },

  productos: (m) => (m.agrupar ? catalogoAgrupado(m) : cuadricula(m)),

  carrito: (m) => {
    const items = m.items.map((i) => el("div", { class: "item" },
      el("div", {},
        el("span", { class: "item-nombre", text: i.nombre }),
        el("span", { class: "item-detalle", text: `${i.cantidad} × ${soles(i.precio)}` })),
      el("span", { class: "item-subtotal", text: soles(i.subtotal) }),
      m.editable
        ? el("button", {
            type: "button", class: "btn-mini quitar", title: "Quitar del carrito",
            "aria-label": `Quitar ${i.nombre} del carrito`,
            onclick: () => enviar({ accion: "eliminar", valor: i.codigo, etiqueta: `Quitar ${i.nombre}` }),
          }, icono("x"))
        : el("span")));
    const restante = m.restante;
    return el("section", { class: "tarjeta", "aria-label": m.titulo },
      el("div", { class: "tarjeta-cab" },
        el("h3", { class: "tarjeta-titulo", text: m.titulo }),
        el("span", { class: "tarjeta-meta", text: `${m.unidades} ${m.unidades === 1 ? "unidad" : "unidades"}` })),
      items,
      el("div", { class: "totales" },
        fila("Subtotal", soles(m.subtotal)),
        fila(`IGV (${m.igv_porcentaje}%)`, soles(m.igv)),
        fila("Total", soles(m.total), "total"),
        fila("Presupuesto", soles(m.presupuesto)),
        fila(restante >= 0 ? "Restante" : "Excede en", soles(Math.abs(restante)), null,
          restante >= 0 ? "positivo" : "negativo")));
  },

  reporte: (m) => el("div", { class: "contenido" },
    el("section", { class: "tarjeta", "aria-label": "Stock bajo" },
      el("div", { class: "tarjeta-cab" },
        el("h3", { class: "tarjeta-titulo", text: "Stock bajo" }),
        el("span", { class: "tarjeta-meta", text: "3 unidades o menos" })),
      m.stock_bajo.length
        ? el("ul", { class: "reporte-lista" }, m.stock_bajo.map((p) => el("li", {},
            el("span", { text: p.nombre }),
            el("span", { class: "pastilla", text: `${p.stock} u.` }))))
        : el("p", { class: "tarjeta-meta", style: "padding:0 16px 14px", text: "Todo bien con el stock." })),
    m.agotados?.length
      ? el("section", { class: "tarjeta", "aria-label": "Agotados" },
          el("div", { class: "tarjeta-cab" },
            el("h3", { class: "tarjeta-titulo", text: "Agotados" }),
            el("span", { class: "tarjeta-meta", text: `${m.agotados.length} productos` })),
          el("ul", { class: "reporte-lista" }, m.agotados.map((p) => el("li", {},
            el("span", { text: p.nombre }),
            el("span", { class: "pastilla pastilla-agotado", text: "0 u." })))))
      : null,
    el("section", { class: "tarjeta", "aria-label": "Resumen por categoría" },
      el("div", { class: "tarjeta-cab" }, el("h3", { class: "tarjeta-titulo", text: "Resumen por categoría" })),
      el("div", { class: "tabla-scroll" },
        el("table", { class: "tabla" },
          el("thead", {}, el("tr", {},
            el("th", { scope: "col", text: "Categoría" }),
            el("th", { scope: "col", text: "Más caro" }),
            el("th", { scope: "col", text: "Más barato" }))),
          el("tbody", {}, m.resumen.map((r) => el("tr", {},
            el("td", {}, r.etiqueta, el("small", { text: `${r.cantidad} productos` })),
            el("td", {}, r.masCaro.nombre, el("small", { text: soles(r.masCaro.precio) })),
            el("td", {}, r.masBarato ? r.masBarato.nombre : "—",
              r.masBarato ? el("small", { text: soles(r.masBarato.precio) }) : null)))))))),
};

function fila(etiqueta, valor, claseFila, claseValor) {
  return el("div", { class: claseFila }, el("span", { text: etiqueta }), el("span", { class: claseValor, text: valor }));
}

/* Estado de stock de un producto para esta sesión:
   agotado   → stock 0 en el inventario (nadie puede agregarlo)
   enCarrito → hay stock, pero el cliente ya tiene todo en su carrito */
function estadoStock(p) {
  if (p.stock <= 0) return { bloqueado: true, texto: "Agotado", motivo: "Producto agotado" };
  if (p.disponible <= 0) return { bloqueado: true, texto: "En carrito", motivo: "Ya tienes todo el stock en tu carrito" };
  return { bloqueado: false };
}

function textoStock(p) {
  return p.stock <= 0 ? "Agotado" : `Stock: ${p.stock}`;
}

function claseStock(p) {
  return "stock" + (p.stock <= 0 ? " stock-agotado" : p.stock <= 3 ? " stock-bajo" : "");
}

function botonAgregar(p, compacto) {
  const est = estadoStock(p);
  const props = {
    type: "button",
    class: compacto ? "btn-mini" : "btn-agregar",
    disabled: est.bloqueado || null,
    title: est.bloqueado ? est.motivo : "Agregar al carrito",
    "aria-label": est.bloqueado ? `${p.nombre}: ${est.motivo.toLowerCase()}` : `Agregar ${p.nombre} al carrito`,
    onclick: () => enviar({ accion: "agregar", valor: p.codigo, etiqueta: `Agregar ${p.nombre}` }),
  };
  if (compacto) return el("button", props, icono(est.bloqueado ? "x" : "plus"));
  return est.bloqueado
    ? el("button", props, est.texto)
    : el("button", props, icono("plus"), "Agregar");
}

function cuadricula(m) {
  const tarjetas = m.productos.map((p) => el("article", { class: "producto" + (p.stock <= 0 ? " producto-agotado" : "") },
    el("span", { class: "producto-etq", text: `${p.marca} · ${p.uso}` }),
    el("h4", { class: "producto-nombre", text: p.nombre }),
    el("span", { class: "producto-precio", text: soles(p.precio) }),
    el("div", { class: "producto-pie" },
      el("span", { class: claseStock(p), text: textoStock(p) }),
      m.agregable ? botonAgregar(p, false) : null)));
  return el("section", { "aria-label": m.titulo || "Productos" },
    m.titulo ? el("div", { class: "tarjeta-cab", style: "padding:0 2px 8px" },
      el("h3", { class: "tarjeta-titulo", text: m.titulo }),
      el("span", { class: "tarjeta-meta", text: `${m.productos.length} resultados` })) : null,
    el("div", { class: "productos" }, tarjetas));
}

function catalogoAgrupado(m) {
  const grupos = {};
  for (const p of m.productos) (grupos[p.categoria] ||= []).push(p);
  return el("section", { class: "tarjeta", "aria-label": m.titulo },
    el("div", { class: "tarjeta-cab" },
      el("h3", { class: "tarjeta-titulo", text: m.titulo }),
      el("span", { class: "tarjeta-meta", text: `${m.productos.length} productos` })),
    Object.entries(grupos).map(([cat, lista]) => el("div", { class: "grupo" },
      el("h4", { class: "grupo-titulo", text: ETIQUETAS[cat] || cat }),
      lista.map((p) => el("div", { class: "fila" + (p.stock <= 0 ? " producto-agotado" : "") },
        el("div", {},
          el("span", { class: "fila-nombre", text: p.nombre }),
          el("span", { class: "fila-sub" }, `${p.marca} · ${p.uso} · `,
            el("span", { class: claseStock(p), text: p.stock <= 0 ? "agotado" : `stock ${p.stock}` }))),
        el("span", { class: "fila-precio", text: soles(p.precio) }),
        m.agregable ? botonAgregar(p, true) : el("span"))))));
}

/* ───────── composer y barra ───────── */

function actualizarBoton() {
  btnEnviar.disabled = ocupado || !entrada.value.trim();
}

function autoAltura() {
  entrada.style.height = "auto";
  entrada.style.height = Math.min(entrada.scrollHeight, 160) + "px";
}

entrada.addEventListener("input", () => { autoAltura(); actualizarBoton(); });
entrada.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    form.requestSubmit();
  }
});
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const texto = entrada.value.trim();
  if (!texto || ocupado) return;
  entrada.value = "";
  autoAltura();
  actualizarBoton();
  enviar({ texto });
});

btnCarrito.addEventListener("click", () => enviar({ accion: "carrito", etiqueta: "Ver carrito" }));
$("#btn-nueva").addEventListener("click", () => { if (!ocupado) iniciar(); });
$("#btn-tema").addEventListener("click", () => {
  const raiz = document.documentElement;
  const oscuro = raiz.dataset.theme
    ? raiz.dataset.theme === "dark"
    : matchMedia("(prefers-color-scheme: dark)").matches;
  raiz.dataset.theme = oscuro ? "light" : "dark";
  try { localStorage.setItem("techpos-tema", raiz.dataset.theme); } catch (_) {}
});

iniciar().then(() => entrada.focus());
