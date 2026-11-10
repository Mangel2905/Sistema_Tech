# TechPOS · Sistema de recomendación tecnológica

Asesor conversacional que recomienda productos tecnológicos según el presupuesto,
la categoría, el uso y la marca preferida del cliente. Integra tres lenguajes:

| Capa | Lenguaje | Responsabilidad |
|---|---|---|
| Reglas / inferencia | **Prolog** (`prolog/`) | Decide qué recomendar: presupuesto, categoría, uso, marca, stock y alternativas (+20%) |
| Catálogo / reportes | **Scala** (`scala/`) | Fuente única del catálogo (nombres, marcas, precios, stock) y reportes de inventario |
| Integración / interfaz | **Python** (`python/`) | Backend FastAPI, motor conversacional, carrito con IGV, consola y frontend web |

```
Navegador (python/web)  ──HTTP/JSON──►  FastAPI (python/src/api)
                                          └─ Motor conversacional (python/src/chatbot)
                                               ├─ subprocess ► swipl  prolog/consultas.pl     (recomendaciones)
                                               └─ subprocess ► java -jar Sistema-Tech-assembly (catálogo JSON, reportes)
```

## Requisitos

- Python 3.10+
- SWI-Prolog (`swipl` en el PATH)
- Java 11+ y sbt (solo para recompilar Scala)

## Puesta en marcha

```bash
# 1. Compilar el JAR de Scala (solo la primera vez o si cambias código Scala)
cd scala
sbt assembly

# 2. Instalar dependencias de Python
cd ../python
pip install -r requirements.txt

# 3a. Chatbot web
cd src
uvicorn api.app:app --reload
#    → abrir http://127.0.0.1:8000   (API interactiva en http://127.0.0.1:8000/docs)

# 3b. Versión de consola (menú clásico)
python main.py
```

## Pruebas

```bash
cd python
python -m pytest -q
```

Verifican el escape de comillas hacia Prolog, que el catálogo de Prolog y el de Scala coincidan, la regla del IGV
y una conversación completa por HTTP (registro → recomendaciones → carrito → reportes → compra).

## API

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/chat/sesion` | Inicia una conversación y devuelve el saludo |
| POST | `/api/chat` | `{sesion_id, texto?, accion?, valor?}` → mensajes + opciones rápidas |
| GET | `/api/catalogo?categoria=` | Catálogo (Scala) |
| GET | `/api/reportes` | Stock bajo y resumen por categoría (Scala) |
| POST | `/api/recomendaciones` | `{presupuesto, categoria, uso, marca?}` → recomendaciones (Prolog) |
| GET | `/api/salud` | Estado de Prolog y Scala |

El chat responde con mensajes tipados (`texto`, `aviso`, `productos`, `carrito`, `reporte`) y `opciones`
(botones de respuesta rápida). Así el frontend solo dibuja y toda la lógica queda en Python.

## Reglas de negocio

- **Recomendación (Prolog):** precio ≤ presupuesto, misma categoría y uso, con stock y la marca pedida (o cualquiera).
- **Alternativas (Prolog):** si no hay coincidencias exactas, productos entre el presupuesto y el presupuesto + 20 %.
- **Carrito (Python y Scala, misma regla):** IGV = 18 % del subtotal (truncado), TOTAL = subtotal + IGV,
  RESTANTE = presupuesto − TOTAL.
