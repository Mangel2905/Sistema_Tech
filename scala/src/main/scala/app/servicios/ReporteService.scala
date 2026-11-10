package app.servicios

import app.modelos.Producto

object ReporteService {

    case class ResumenCategoria(categoria: String, cantidad: Int, masCaro: Producto, masBarato: Option[Producto])

    def stockBajo(productos: List[Producto]): List[Producto] =
        productos.filter(p => p.stock > 0 && p.stock <= 3).sortBy(_.stock)

    def agotados(productos: List[Producto]): List[Producto] =
        productos.filter(_.stock <= 0)

    def mostrarAgotados(productos: List[Producto]): Unit = {
        val lista = agotados(productos)
        if (lista.nonEmpty) {
            println("\n  === Agotados ===")
            lista.foreach(p => println(f"  ${p.nombre}%-32s  S/${p.precio}"))
        }
    }

    def resumen(productos: List[Producto]): List[ResumenCategoria] =
        productos.groupBy(_.categoria).toList.sortBy(_._1).map { case (cat, lista) =>
            ResumenCategoria(cat, lista.size, lista.maxBy(_.precio), lista.filter(_.stock > 0).minByOption(_.precio))
        }

    def mostrarStockBajo(productos: List[Producto]): Unit = {
        println("\n  === Stock bajo (3 unidades o menos) ===")
        val lista = stockBajo(productos)
        if (lista.isEmpty) println("  Todo bien con el stock.")
        else lista.foreach(p => println(f"  ${p.nombre}%-32s  stock: ${p.stock}  S/${p.precio}"))
    }

    def mostrarResumen(productos: List[Producto]): Unit = {
        println("\n  === Resumen por categoria ===")
        resumen(productos).foreach { r =>
            println(s"\n  ${r.categoria} (${r.cantidad} productos)")
            println(f"    Mas caro:   ${r.masCaro.nombre}%-30s S/${r.masCaro.precio}")
            r.masBarato.foreach(p => println(f"    Mas barato: ${p.nombre}%-30s S/${p.precio}"))
        }
    }
}
