// ============================================
// Main.scala
// Punto de entrada principal del sistema
// Gestiona el flujo de interacción con
// el usuario por consola
// ============================================

package app

import app.modelos.{Cliente, Producto}
import app.servicios.{ClienteService, ProductoService}
import scala.io.StdIn.readLine

object Main extends App {

  // Bienvenida
  println("====================================")
  println("  Sistema de Recomendación Tech 🤖")
  println("====================================")

  // Solicitar datos del cliente
  val nombre      = readLine("Ingresa tu nombre: ")
  val presupuesto = readLine("Presupuesto en soles: ").toInt
  val categoria   = readLine("Categoría (laptop/celular/tablet/audifono/smartwatch/accesorio): ")
  val uso         = readLine("Uso (estudio/trabajo/gaming/casual): ")

  // Crear cliente con los datos ingresados
  val cliente = Cliente(nombre, presupuesto, categoria, uso)

  // Mostrar datos del cliente
  ClienteService.mostrar(cliente)

  // Catálogo de productos tecnológicos
  val productos = List(
    // Laptops
    Producto("Laptop Lenovo IdeaPad", "Lenovo", 1800, "laptop", "estudio"),
    Producto("Laptop HP 15",          "HP",     1500, "laptop", "estudio"),
    Producto("Laptop Asus VivoBook",  "Asus",   1900, "laptop", "trabajo"),
    Producto("Laptop Dell Inspiron",  "Dell",   2200, "laptop", "trabajo"),
    // Celulares
    Producto("iPhone 14",             "Apple",   3200, "celular", "casual"),
    Producto("Samsung Galaxy A54",    "Samsung", 1200, "celular", "casual"),
    Producto("Xiaomi Redmi Note 12",  "Xiaomi",   800, "celular", "casual"),
    // Tablets
    Producto("iPad Air",              "Apple",  2800, "tablet", "estudio"),
    Producto("Samsung Galaxy Tab A8", "Samsung", 900, "tablet", "estudio"),
    // Audifonos
    Producto("Sony WH-1000XM5",       "Sony",   850, "audifono", "trabajo"),
    Producto("JBL Tune 510BT",        "JBL",    250, "audifono", "casual"),
    // Smartwatches
    Producto("Apple Watch SE",        "Apple",  1100, "smartwatch", "casual"),
    Producto("Samsung Galaxy Watch",  "Samsung", 750, "smartwatch", "casual"),
    // Accesorios
    Producto("Teclado Redragon K552", "Redragon", 250, "accesorio", "gaming"),
    Producto("Mouse Logitech G305",   "Logitech", 180, "accesorio", "gaming")
  )

  // Filtrar productos según perfil del cliente
  val filtrados = ProductoService.filtrar(productos, cliente)

  // Mostrar productos filtrados
  ProductoService.mostrar(filtrados)
}