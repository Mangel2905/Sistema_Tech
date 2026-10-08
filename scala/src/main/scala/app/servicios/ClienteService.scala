// ============================================
// ClienteService.scala
// Servicio que gestiona las operaciones
// relacionadas al cliente
// ============================================

package app.servicios

import app.modelos.Cliente

object ClienteService {

  // Muestra los datos del cliente en consola
  def mostrar(cliente: Cliente): Unit = {
    println("\n====================================")
    println("   Datos del Cliente")
    println("====================================")
    println(s"Nombre       : ${cliente.nombre}")
    println(s"Presupuesto  : S/. ${cliente.presupuesto}")
    println(s"Categoría    : ${cliente.categoria}")
    println(s"Uso principal: ${cliente.uso}")
    println("====================================")
  }
}