package app

import app.modelos.ItemCarrito
import app.servicios._

object Main extends App {

    // Modo comando: Python llama con argumentos
    // sbt run -- listar
    // sbt run -- listar laptop
    // sbt run -- reporte
    if (args.nonEmpty) {
        args(0) match {
            case "listar" =>
                if (args.length > 1) CatalogoService.mostrarTabla(CatalogoService.porCategoria(args(1)))
                else                 CatalogoService.mostrarTabla(CatalogoService.productos)

            case "reporte" =>
                ReporteService.mostrarStockBajo(CatalogoService.productos)
                ReporteService.mostrarAgotados(CatalogoService.productos)
                ReporteService.mostrarResumen(CatalogoService.productos)

            // Salida JSON para Python (fuente unica del catalogo)
            // java -jar app.jar json            -> catalogo completo
            // java -jar app.jar json laptop     -> solo una categoria (con stock)
            // java -jar app.jar reporte-json    -> stock bajo + resumen
            case "json" =>
                val lista =
                    if (args.length > 1) CatalogoService.porCategoria(args(1))
                    else                 CatalogoService.productos
                println(JsonService.productos(lista))

            case "reporte-json" =>
                println(JsonService.reporte(CatalogoService.productos))

            case _ =>
                println(s"Comando desconocido: ${args(0)}")
        }
        System.exit(0)
    }

    // Modo interactivo: se usa directo sin Python
    println("=" * 50)
    println("     TECHPOS - Sistema de Recomendacion")
    println("=" * 50)

    var carrito: List[ItemCarrito] = List()
    val cliente = ClienteService.registrar()
    ClienteService.mostrar(cliente)

    var seguir = true
    while (seguir) {
        println("\n  ---- MENU ----")
        println("  1. Ver catalogo")
        println("  2. Ver por categoria")
        println("  3. Agregar al carrito")
        println("  4. Ver carrito")
        println("  5. Eliminar del carrito")
        println("  6. Reportes")
        println("  7. Salir")
        print("  Opcion: ")

        scala.io.StdIn.readLine().trim match {
            case "1" =>
                CatalogoService.mostrarTabla(CatalogoService.productos)

            case "2" =>
                val cat = Validacion.pedirOpcion(
                    s"  Categoria (${CatalogoService.categorias.mkString("/")}): ",
                    CatalogoService.categorias
                )
                CatalogoService.mostrarTabla(CatalogoService.porCategoria(cat))

            case "3" =>
                print("  Codigo del producto: ")
                val codigo = scala.io.StdIn.readLine().trim
                CatalogoService.buscarPorCodigo(codigo) match {
                    case None    => println("  Codigo no encontrado.")
                    case Some(p) if p.stock <= 0 => println(s"  ${p.nombre} esta agotado.")
                    case Some(p) =>
                        val cant = Validacion.pedirEntero("  Cantidad: ", 1, p.stock)
                        CarritoService.agregar(carrito, p, cant) match {
                            case Left(e)  => println(s"  Error: $e")
                            case Right(c) => carrito = c; println(s"  Agregado: ${p.nombre}")
                        }
                }

            case "4" =>
                CarritoService.mostrar(carrito, cliente.presupuesto)

            case "5" =>
                CarritoService.mostrar(carrito, cliente.presupuesto)
                print("  Codigo a eliminar: ")
                val cod = scala.io.StdIn.readLine().trim
                carrito = CarritoService.eliminar(carrito, cod)
                println("  Eliminado.")

            case "6" =>
                ReporteService.mostrarStockBajo(CatalogoService.productos)
                ReporteService.mostrarAgotados(CatalogoService.productos)
                ReporteService.mostrarResumen(CatalogoService.productos)

            case "7" =>
                seguir = false
                println("\n  Hasta luego!")

            case _ => println("  Opcion invalida.")
        }
    }
}