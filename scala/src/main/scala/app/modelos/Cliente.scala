// ============================================
// Cliente.scala
// Modelo que representa a un cliente
// del sistema de recomendación tech
// ============================================

package app.modelos

// Case class que define la estructura de un Cliente
// nombre     → nombre del cliente
// presupuesto → cuánto puede gastar en soles
// categoria  → tipo de producto que busca
// uso        → para qué usará el producto
case class Cliente(
  nombre: String,
  presupuesto: Int,
  categoria: String,
  uso: String
)