
package app.servicios

import app.modelos.{Cliente, Producto}

object ProductoService {

  // Filtra productos 
  def filtrar(productos: List[Producto], cliente: Cliente): List[Producto] = {
    productos
      .filter(p => p.precio <= cliente.presupuesto)  // filtrado por presupuesto
      .filter(p => p.categoria == cliente.categoria)  // filtrado por categoria
  }

  // Muestra la lista de productos
  def mostrar(productos: List[Producto]): Unit = {
    if (productos.isEmpty) {
      println("\n  No se encontraron productos en tu rango.")
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