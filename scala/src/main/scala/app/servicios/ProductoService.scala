// ============================================
// ProductoService.scala
// Servicio que gestiona las operaciones
// relacionadas a los productos tecnológicos
// ============================================

package app.servicios

import app.modelos.{Cliente, Producto}

object ProductoService {

  // Filtra productos según presupuesto y categoría del cliente
  def filtrar(productos: List[Producto], cliente: Cliente): List[Producto] = {
    productos
      .filter(p => p.precio <= cliente.presupuesto)  // filtra por presupuesto
      .filter(p => p.categoria == cliente.categoria)  // filtra por categoría
  }

  // Muestra la lista de productos disponibles en consola
  def mostrar(productos: List[Producto]): Unit = {
    if (productos.isEmpty) {
      println("\n⚠️  No se encontraron productos en tu rango.")
    } else {
      println("\n====================================")
      println("   Productos Disponibles")
      println("====================================")
      productos.foreach { p =>
        println(s"- ${p.nombre} | ${p.marca} | S/. ${p.precio} | Uso: ${p.uso}")
      }
      println("====================================")
    }
  }
}