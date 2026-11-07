package app.modelos

case class Producto(
    codigo: String,
    nombre: String,
    marca: String,
    precio: Int,
    categoria: String,
    uso: String,
    stock: Int
)