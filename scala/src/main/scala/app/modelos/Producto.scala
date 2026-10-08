// ============================================
// Producto.scala
// Modelo que representa un producto
// tecnológico del catálogo del sistema
// ============================================

package app.modelos

// Case class que define la estructura de un Producto
// nombre    → nombre del producto
// marca     → marca del producto
// precio    → precio en soles
// categoria → tipo de producto (laptop, celular, etc)
// uso       → uso recomendado (estudio, trabajo, gaming, casual)
case class Producto(
  nombre: String,
  marca: String,
  precio: Int,
  categoria: String,
  uso: String
)