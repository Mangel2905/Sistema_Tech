package app.servicios

import app.modelos.Producto

object ReporteService {

    def mostrarStockBajo(productos: List[Producto]): Unit = {
        println("\n  === Stock bajo (menos de 3 unidades) ===")
        val lista = productos.filter(p => p.stock > 0 && p.stock <= 3).sortBy(_.stock)
        if (lista.isEmpty) println("  Todo bien con el stock.")
        else lista.foreach(p => println(f"  ${p.nombre}%-32s  stock: ${p.stock}  S/${p.precio}"))
    }

    def mostrarResumen(productos: List[Producto]): Unit = {
        println("\n  === Resumen por categoria ===")
        productos.groupBy(_.categoria).toList.sortBy(_._1).foreach { case (cat, lista) =>
            val masCaro   = lista.maxBy(_.precio)
            val masBarato = lista.filter(_.stock > 0).minByOption(_.precio)
            println(s"\n  $cat (${lista.size} productos)")
            println(f"    Mas caro:   ${masCaro.nombre}%-30s S/${masCaro.precio}")
            masBarato.foreach(p => println(f"    Mas barato: ${p.nombre}%-30s S/${p.precio}"))
        }
    }
}