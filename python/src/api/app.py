"""Backend FastAPI de TechPOS.

Ejecutar (desde python/src):
    uvicorn api.app:app --reload
Luego abrir http://127.0.0.1:8000  (documentacion interactiva en /docs)
"""
import os
from contextlib import asynccontextmanager
from typing import Literal, Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from chatbot.motor import AlmacenSesiones, Motor
from chatbot.texto import CATEGORIAS, USOS
from integracion import integrador, scala_service
from integracion.prolog_service import PrologError
from integracion.scala_service import ScalaError
from modelos.cliente import Cliente

WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../web"))

motor = Motor()
sesiones = AlmacenSesiones()


@asynccontextmanager
async def lifespan(_app):
    # Precarga el catalogo y los reportes de Scala (arrancar la JVM tarda ~1 s).
    try:
        scala_service.catalogo()
        scala_service.reportes()
    except ScalaError as e:
        print(f"[TechPOS] Aviso: no se pudo precargar el catalogo Scala: {e}")
    yield


app = FastAPI(
    title="TechPOS API",
    description="Chatbot de recomendación tecnológica: Python (FastAPI) + Prolog (reglas) + Scala (catálogo).",
    version="1.0.0",
    lifespan=lifespan,
)


# ───────────── modelos de entrada ─────────────

class MensajeChat(BaseModel):
    sesion_id: str
    texto: Optional[str] = Field(None, max_length=500)
    accion: Optional[str] = Field(None, max_length=40)
    valor: Optional[Union[int, str]] = None


class PerfilBusqueda(BaseModel):
    nombre: str = Field("cliente", max_length=40)
    presupuesto: int = Field(..., ge=1, le=999999)
    categoria: Literal[tuple(CATEGORIAS)]
    uso: Literal[tuple(USOS)]
    marca: str = Field("ninguna", max_length=30)


def _error_servicio(e):
    raise HTTPException(status_code=503, detail=str(e))


# ───────────── chat ─────────────

@app.post("/api/chat/sesion", tags=["chat"], summary="Inicia una conversación nueva")
def nueva_sesion():
    return motor.bienvenida(sesiones.crear())


@app.post("/api/chat", tags=["chat"], summary="Envía un mensaje o una acción al asesor")
def chat(msg: MensajeChat):
    s = sesiones.obtener(msg.sesion_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada o expirada.")
    return motor.procesar(s, texto=msg.texto, accion=msg.accion, valor=msg.valor)


# ───────────── REST directo (útil para pruebas y otros clientes) ─────────────

@app.get("/api/catalogo", tags=["catalogo"], summary="Catálogo (Scala)")
def catalogo(categoria: Optional[Literal[tuple(CATEGORIAS)]] = None):
    try:
        return scala_service.catalogo(categoria)
    except ScalaError as e:
        _error_servicio(e)


@app.get("/api/reportes", tags=["catalogo"], summary="Stock bajo y resumen por categoría (Scala)")
def reportes():
    try:
        return scala_service.reportes()
    except ScalaError as e:
        _error_servicio(e)


@app.post("/api/recomendaciones", tags=["recomendaciones"], summary="Recomendaciones (Prolog)")
def recomendaciones(perfil: PerfilBusqueda):
    cliente = Cliente(perfil.nombre, perfil.presupuesto, perfil.categoria, perfil.uso,
                      perfil.marca.strip().lower() or "ninguna")
    try:
        productos, es_alternativa = integrador.buscar_recomendaciones(cliente)
    except (PrologError, ScalaError) as e:
        _error_servicio(e)
    return {"es_alternativa": es_alternativa, "productos": productos}


@app.get("/api/salud", tags=["sistema"], summary="Estado de Prolog y Scala")
def salud():
    estado = {}
    try:
        estado["scala"] = f"ok ({len(scala_service.catalogo())} productos)"
    except ScalaError as e:
        estado["scala"] = f"error: {e}"
    try:
        integrador.prolog_service.verificar_stock("laptop_acer_asp3")
        estado["prolog"] = "ok"
    except PrologError as e:
        estado["prolog"] = f"error: {e}"
    return estado


# ───────────── frontend ─────────────

if os.path.isdir(WEB_DIR):
    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def inicio():
        return FileResponse(os.path.join(WEB_DIR, "index.html"))
