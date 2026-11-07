package app.servicios

import scala.annotation.tailrec

object Validacion {

    @tailrec
    def pedirOpcion(pregunta: String, validas: List[String]): String = {
        print(pregunta)
        val entrada = scala.io.StdIn.readLine().trim.toLowerCase
        if (validas.contains(entrada)) entrada
        else {
            println(s"  Opcion invalida. Elige: ${validas.mkString(", ")}")
            pedirOpcion(pregunta, validas)
        }
    }

    @tailrec
    def pedirPresupuesto(pregunta: String): Int = {
        print(pregunta)
        scala.io.StdIn.readLine().trim.toIntOption match {
            case Some(n) if n > 0 => n
            case Some(_) =>
                println("  Debe ser mayor a 0.")
                pedirPresupuesto(pregunta)
            case None =>
                println("  Solo numeros. Ejemplo: 2000")
                pedirPresupuesto(pregunta)
        }
    }

    @tailrec
    def pedirTexto(pregunta: String): String = {
        print(pregunta)
        val entrada = scala.io.StdIn.readLine().trim
        if (entrada.nonEmpty) entrada
        else {
            println("  Campo obligatorio.")
            pedirTexto(pregunta)
        }
    }

    @tailrec
    def pedirEntero(pregunta: String, minimo: Int, maximo: Int): Int = {
        print(pregunta)
        scala.io.StdIn.readLine().trim.toIntOption match {
            case Some(n) if n >= minimo && n <= maximo => n
            case _ =>
                println(s"  Debe ser entre $minimo y $maximo.")
                pedirEntero(pregunta, minimo, maximo)
        }
    }
}