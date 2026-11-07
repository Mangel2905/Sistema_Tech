package app.servicios

import app.modelos.{Producto, ItemCarrito}

object CarritoService {

    val IGV = 0.18

    def agregar(carrito: List[ItemCarrito], producto: Producto, cantidad: Int): Either[String, List[ItemCarrito]] = {
        val yaEnCarrito = carrito.filter(_.producto.codigo == producto.codigo).map(_.cantidad).sum
        if (yaEnCarrito + cantidad > producto.stock)
            Left(s"Stock insuficiente. Disponible: ${producto.stock}, ya tienes: $yaEnCarrito.")
        else {
            val nuevo = carrito.find(_.producto.codigo == producto.codigo) match {
                case Some(_) => carrito.map(i => if (i.producto.codigo == producto.codigo) i.copy(cantidad = i.cantidad + cantidad) else i)
                case None    => carrito :+ ItemCarrito(producto, cantidad)
            }
            Right(nuevo)
        }
    }

    def eliminar(carrito: List[ItemCarrito], codigo: String): List[ItemCarrito] =
        carrito.filterNot(_.producto.codigo == codigo)

    def subtotal(carrito: List[ItemCarrito]): Int  = carrito.map(_.subtotal).sum
    def igv(carrito: List[ItemCarrito]): Int       = (subtotal(carrito) * IGV).toInt
    def total(carrito: List[ItemCarrito]): Int     = subtotal(carrito) + igv(carrito)
    def restante(presupuesto: Int, carrito: List[ItemCarrito]): Int = presupuesto - subtotal(carrito)

    def mostrar(carrito: List[ItemCarrito], presupuesto: Int): Unit = {
        if (carrito.isEmpty) { println("  Carrito vacio."); return }
        println(f"\n  ${"#"}%3s  ${"Producto"}%-32s ${"Precio"}%8s  Cant  Subtotal")
        println("  " + "-" * 62)
        carrito.zipWithIndex.foreach { case (item, i) =>
            println(f"  ${i+1}%3d  ${item.producto.nombre}%-32s S/${item.producto.precio}%6d  ${item.cantidad}%4d  S/${item.subtotal}%6d")
        }
        println("  " + "-" * 62)
        println(f"  Subtotal:   S/${subtotal(carrito)}%8d")
        println(f"  IGV (18%%): S/${igv(carrito)}%8d")
        println(f"  TOTAL:      S/${total(carrito)}%8d")
        val rest = restante(presupuesto, carrito)
        if (rest >= 0) println(f"  Restante:   S/$rest%8d")
        else           println(f"  EXCEDE:     S/${-rest}%8d")
    }
}